# app/mongodb/service.py
from datetime import datetime, timezone
import mimetypes
from typing import List
from pathlib import Path
from fastapi import Depends, HTTPException, status, UploadFile

from app.core.config.project_config import settings
from app.core.utils.common_utils import get_path_to_root
from app.mongodb.config import settings
from app.mongodb.models import FileListResponse, FileResponse
from app.mongodb.repository import ImageRepository
from app.mongodb.utils import (file_name, image_aligning, ContentTypeDetector, read_image_generator,
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
                                  upload_dir: str
                                  ):
        """ прямая загрузка файлов
            из upload_dir
        """
        try:
            image_dir = get_path_to_root(upload_dir)
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
            image_paths = []  # cписок файлов изображений с путями
            for n, file_path in enumerate(image_dir.iterdir()):
                if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                    image_paths.append(file_path)
            # запускаем
            for m, upload_file in enumerate(read_image_generator(image_paths)):
                try:
                    content = await upload_file.read()
                    filename = upload_file.filename
                except Exception as e:
                    raise Exception(f'filename = upload_file.filename. {e}')
                # удаляем фон 3 способа доработать
                try:
                    # content = make_transparent_white_bg(content)
                    content = remove_background(content)
                    # content = remove_background_with_mask(content)
                    content_type = 'image/png'
                    filename = f'{filename.rsplit('.', 1)[0]}.png'
                except Exception as e:
                    raise Exception(f'Удаление фона не получилось для {filename}. {e}. Оставляем без изменения')
                # подгоняем размер
                try:
                    if len(content) > 8 * 1024 * 1024:
                        content = image_aligning(content)
                except Exception as e:
                    raise Exception(f'Изменение размера не получилось для {filename}. {e}. Оставляем без изменения')
                description = f'импортированный файл {datetime.now(timezone.utc)}'
                
                
                _id = await self.image_repository.create_image(filename, content, content_type, description)
            
        except Exception as e:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = f"error: {e}"
                    )
        return {'result': m+1}
        
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