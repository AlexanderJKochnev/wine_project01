# app/mongodb/service.py
from datetime import datetime
from typing import List

from fastapi import Depends, HTTPException, status

from app.core.config.project_config import settings
from app.mongodb.config import settings
from app.mongodb.models import FileListResponse, FileResponse
from app.mongodb.repository import ImageRepository
from app.mongodb.utils import (file_name)


class ImageService:
    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository


    async def upload_image(self,
                           filename: str,
                           content: bytes,
                           description: str,
                           # drink_id: int
                           ):
        try:
            pass
            # content = image_aligning(content)
        except Exception:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = "image aligning fault"
                    )
        try:
            pass
            # content = remove_background_with_mask(content)
        except Exception:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = "remove background fault"
                    )
        if len(content) > 8 * 1024 * 1024:
            # сюда вставить обработку изображения
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        filename=file_name(filename, settings.LENGTH_RANDOM_NAME, '.png')
        return await self.image_repository.create_image(filename, content, description)  # , drink_id)

    async def get_image(self,
                        image_id: str,
                        # drink_id: int
                        ):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        # if image["drink_id"] != drink_id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
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