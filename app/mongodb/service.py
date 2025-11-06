# app/mongodb/service.py
import asyncio
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from typing import List, Tuple

from fastapi import Depends, HTTPException, status, UploadFile

# from app.core.config.project_config import settings
from app.core.utils.io_utils import get_filepath_from_dir
from app.mongodb.config import settings
from app.mongodb.models import FileListResponse, FileResponse
from app.mongodb.repository import ImageRepository
from app.mongodb.utils import (file_name, image_aligning, make_transparent_white_bg, read_image_generator,
                               )
# from app.core.memcached_cache import cache_image_memcached
from app.mongodb.repository import ThumbnailImageRepository


# delta = (datetime.now(timezone.utc) - relativedelta(years=2)).isoformat()
delta = datetime.now(timezone.utc) - relativedelta(years=2)


class ImageService:
    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository

    async def upload_image(self,
                           file: UploadFile,
                           description: str,
                           ):
        try:
            content = await file.read()
            content = make_transparent_white_bg(content)
            content_type = "image/png"
            # content = remove_background_with_mask(content)
            if len(content) > 8 * 1024 * 1024:
                content = image_aligning(content)
            filename = file_name(file.filename, settings.LENGTH_RANDOM_NAME, '.png')
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"image aligning fault: {e}"
            )
        _id = await self.image_repository.create_image(filename, content, content_type, description)
        return _id, filename

    async def direct_upload_image(self, limit: int = 3):
        """ прямая загрузка файлов
            из upload_dir
            limit - ограничение на количество загружаемых файлов (в основном для целей тестирования)
        """
        try:
            # upload_dir = settings.UPLOAD_DIR
            lost_images = []  # список потерянных файлов
            image_paths = get_filepath_from_dir()
            n = len(image_paths)
            # запускаем
            for m, upload_file in enumerate(read_image_generator(image_paths)):
                try:
                    content = await upload_file.read()
                    filename = upload_file.filename
                except Exception as e:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"upload_file fault: {e}"
                    )
                # удаляем фон 3 способа доработать
                try:
                    # content = make_transparent_white_bg(content)
                    # content = remove_background(content)
                    # content = remove_background_with_mask(content)
                    content_type = 'image/png'
                    filename = f"{filename.rsplit('.', 1)[0]}.png"
                except Exception as e:
                    HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Удаление фона не получилось для {filename}. {e}. Оставляем без изменения')
                # подгоняем размер
                try:
                    if len(content) > 8 * 1024 * 1024:
                        content = image_aligning(content)
                except Exception as e:
                    HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Изменение размера не получилось для {filename}. {e}. Оставляем без изменения'
                    )
                description = f'импортированный файл {datetime.now(timezone.utc)}'

                id = await self.image_repository.create_image(filename, content, content_type, description)
                if not id:
                    lost_images.append(filename)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"error: {e}"
            )
        result = {'number of images': n + 1,
                  'loaded images': m + 1}
        if lost_images:
            result['lost images': lost_images]
        return result

    async def get_image(self,
                        image_id: str
                        ) -> FileResponse:
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        # if image["drink_id"] != drink_id:
        #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return image

    async def get_image_by_filename(self, filename: str) -> FileResponse:
        image = await self.image_repository.get_image_by_filename(filename)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Image "{filename}" not found')
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
                images=images, total=total, has_more=has_more
            )

        except Exception as e:
            raise Exception(f"Service error: {str(e)}")

    async def get_recent_images(self, hours: int = 24) -> List[FileResponse]:
        """
        Упрощенный метод для получения изображений за последние N часов
        """
        from datetime import datetime, timedelta

        after_date = datetime.utcnow() - timedelta(hours=hours)
        return await self.image_repository.get_images_after_date(after_date)

    async def get_images_list_after_date(
        self, after_date: datetime = delta
    ) -> Tuple:
        """
            возвращает кортеж кортежей  (image_file_name, image_id)...
        """
        try:
            images = await self.image_repository.get_images_after_date_nopage(
                after_date
            )
            return images
        except Exception as e:
            raise Exception(f"Service error: {str(e)}")


class ThumbnailImageService:
    def __init__(self, repository: ThumbnailImageRepository = Depends()):
        self.image_repository = repository

    async def upload_image(self, file, description: str = None):
        """Загрузка изображения с созданием thumbnail'а"""
        content = await file.read()

        result = await self.image_repository.create_image(
            filename=file.filename, content=content,
            content_type=file.content_type, description=description
        )

        return result["id"], file.filename, result["has_thumbnail"]

    # @cache_image_memcached(prefix='full_image', expire=3600, key_params=['file_id'])
    async def get_full_image(self, file_id: str) -> dict:
        """Получить полноразмерное изображение (для DetailView)"""
        image_data = await self.image_repository.get_image(file_id, include_content=True)
        if not image_data or "content" not in image_data:
            raise HTTPException(status_code=404, detail="Image not found")
        return {"content": image_data["content"], "filename": image_data["filename"],
                "content_type": image_data.get("content_type", "image/png"), "from_cache": False}

    # @cache_image_memcached(prefix='thumbnail', expire=3600, key_params=['file_id'])
    async def get_thumbnail(self, file_id: str) -> dict:
        """Получить thumbnail (для списков)"""
        image_data = await self.image_repository.get_thumbnail(file_id)
        if not image_data or "thumbnail" not in image_data:
            # Если thumbnail нет, создаем его на лету (и кэшируем)
            full_image = await self.get_full_image(file_id)
            thumbnail_content = self.image_repository._create_thumbnail_png(full_image["content"])

            if thumbnail_content:
                # Сохраняем thumbnail в базу асинхронно
                asyncio.create_task(
                    self.image_repository.update_image_with_thumbnail(file_id, thumbnail_content)
                )
                return {"content": thumbnail_content, "filename": f"thumb_{image_data['filename']}",
                        "content_type": "image/png", "from_cache": False}
            else:
                # Если не удалось создать thumbnail, возвращаем оригинал
                return full_image

        return {"content": image_data["thumbnail"], "filename": f"thumb_{image_data['filename']}",
                "content_type": image_data.get("thumbnail_type", "image/png"), "from_cache": False}

    # @cache_image_memcached(prefix='thumbnail', expire=3600, key_params=['filename'])
    async def get_thumbnail_by_filename(self, filename: str) -> dict:
        """Получить thumbnail по имени файла"""
        image_data = await self.image_repository.get_thumbnail_by_filename(filename)
        if not image_data or "thumbnail" not in image_data:
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        return {"content": image_data["thumbnail"], "filename": f"thumb_{image_data['filename']}",
                "content_type": image_data.get("thumbnail_type", "image/png"), "from_cache": False}

    async def get_images_after_date(self, after_date: datetime, page: int, per_page: int):
        """Получить список изображений (только метаданные)"""
        skip = (page - 1) * per_page
        images = await self.image_repository.get_images_after_date(after_date, skip, per_page)
        total = await self.image_repository.count_images_after_date(after_date)

        return {"images": images, "total": total, "has_more": (skip + len(images)) < total}

    # Остальные методы остаются без изменений
    async def get_images_list_after_date(self, after_date: datetime):
        result = await self.image_repository.get_images_after_date_nopage(after_date)
        return result

    async def delete_image(self, file_id: str) -> bool:
        return await self.image_repository.delete_image(file_id)
