# app/mongodb/service.py
from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException, status, UploadFile

from app.core.config.project_config import settings
from app.mongodb.config import settings
from app.mongodb.models import FileListResponse, FileResponse
from app.mongodb.repository import ImageRepository
from app.mongodb.utils import (file_name, image_aligning, ContentTypeDetector,
                               remove_background, remove_background_with_mask, make_transparent_white_bg)


class ImageService:
    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository


    async def upload_image(self,
                           file: UploadFile,
                           description: str,
                           ):
        try:
            # content_type = await ContentTypeDetector.detect(file)
            content = await file.read()
            content = make_transparent_white_bg(content)
            content_type = "image/png"
            # content = remove_background_with_mask(content)
            if len(content) > 8 * 1024 * 1024:
                content = image_aligning(content)
            filename = file_name(file.filename, settings.LENGTH_RANDOM_NAME, '.png')
        except Exception as e:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = f"image aligning fault: {e}"
                    )
        _id = await self.image_repository.create_image(filename, content, content_type, description)
        return _id, filename

    async def direct_upload_image(self,
                                  file: UploadFile,
                                  description: str,
                                  change_name: bool = False,
                                  remove_back: int = 0
                                  ):
        """ прямая загрузка файлов """
        try:
            # content_type = await ContentTypeDetector.detect(file)
            content = await file.read()
            content_type = "image/png"
            match remove_back:
                case 1:
                    content = make_transparent_white_bg(content)
                case 2:
                    content = remove_background(content)
                case 3:
                    content = remove_background_with_mask(content)
                case _:
                    content_type = await ContentTypeDetector.detect(file)
            if len(content) > 8 * 1024 * 1024:
                content = image_aligning(content)
            if change_name:
                filename = file_name(file.filename, settings.LENGTH_RANDOM_NAME, '.png')
            else:
                filename = file.filename
        except Exception as e:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = f"image aligning fault: {e}"
                    )
        _id = await self.image_repository.create_image(filename, content, content_type, description)
        return _id, filename
        
    async def get_image(self,
                        image_id: str
                        ):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        # if image["drink_id"] != drink_id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return image


    async def get_image_by_filename(self, filename: str):
        image = await self.image_repository.get_image_by_filename(filename)
        if not image:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'Image "{filename}" not found')
        return image

    async def delete_image(self,
                           image_id: str,
                           # drink_id: int
                           ):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        # if image["drink_id"] != drink_id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.image_repository.delete_image(image_id)
    
    async def get_images_after_date(
            self, after_date: datetime, page: int = 1, per_page: int = 100
            ) -> FileListResponse:
        """
        Сервисный метод для получения изображений с пагинацией

        Args:
            after_date: Дата для фильтрации
            page: Номер страницы (начинается с 1)
            per_page: Количество элементов на странице

        Returns:
            FileListResponse с изображениями и метаданными
        """
        try:
            # Валидация параметров
            if page < 1:
                page = 1
            per_page = settings.PAGE_DEFAULT
            skip = (page - 1) * per_page
            # Получаем изображения
            images = await self.image_repository.get_images_after_date(
                    after_date, skip, per_page
                    )
            # Получаем общее количество для пагинации
            total = await self.image_repository.count_images_after_date(after_date)
            
            # Проверяем, есть ли еще страницы
            has_more = (skip + len(images)) < total
            
            return FileListResponse(
                    images = images, total = total, has_more = has_more
                    )
        
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")
    
    async def get_recent_images(self, hours: int = 24) -> List[FileResponse]:
        """
        Упрощенный метод для получения изображений за последние N часов
        """
        from datetime import datetime, timedelta
        
        after_date = datetime.utcnow() - timedelta(hours = hours)
        return await self.image_repository.get_images_after_date(after_date)