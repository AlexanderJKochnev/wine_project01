# app/mongodb/repository.py
from bson import ObjectId, Binary
from datetime import datetime, timezone
from fastapi import Depends, HTTPException
from typing import List, Tuple, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.mongodb.config import get_database
from app.mongodb.models import FileResponse, ImageResponse

import io
from PIL import Image


class ImageRepository:
    def __init__(self, database: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = database
        self.collection = self.db["images"]
        self._indexes_created = False

    async def ensure_indexes(self):
        """Создает индексы при первом использовании репозитория"""
        if not self._indexes_created:
            await self.collection.create_index([("filename", -1)], unique=True)
            await self.collection.create_index([("created_at", -1)])
            await self.collection.create_index([("filename", "text")])  # Текстовый поиск
            self._indexes_created = True
            print("Image repository indexes ensured")

    async def create_image(self, filename: str, content: bytes, content_type: str, description: str) -> str:
        """ сохранение изображения в базе данных"""
        await self.ensure_indexes()
        document = {
            "filename": filename,
            "content": content,
            "description": description,
            "created_at": datetime.now(timezone.utc),
            "size": len(content),
            "content_type": content_type
        }
        result = await self.collection.insert_one(document)
        if hasattr(result, 'inserted_id'):
            return str(result.inserted_id)
        else:
            return None

    async def get_image(self, image_id: str):
        """ получение изображени по _id """
        await self.ensure_indexes()
        return await self.collection.find_one({"_id": ObjectId(image_id)})

    async def get_image_by_filename(self, filename: str):
        return await self.collection.find_one({"filename": filename})

    async def get_images_after_date_nopage(self,
                                           after_date: datetime
                                           ) -> List[Tuple]:
        """
            получение списка изображений
            возвращает список кортежей [(image_path, image_id)...]
        """
        await self.ensure_indexes()
        query = {"created_at": {"$gt": after_date}}
        cursor = self.collection.find(query).sort("created_at", -1)
        images = []
        async for image in cursor:
            images.append((image['filename'], str(image["_id"])))
        return images

    async def get_images_after_date(self,
                                    after_date: datetime,
                                    skip: int = 0,
                                    limit: int = 100) -> List[FileResponse]:
        """ получение постраничного списка изображений с деталями"""
        await self.ensure_indexes()
        query = {"created_at": {"$gt": after_date}}
        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        images = []
        async for image in cursor:
            image["_id"] = str(image["_id"])
            # images.append(image)
            images.append(FileResponse(**image))
        return images

    async def count_images_after_date(self, after_date: datetime) -> int:
        """
        Подсчитывает количество изображений, созданных после указанной даты
        """
        try:
            query = {"created_at": {"$gt": after_date}}
            return await self.collection.count_documents(query)
        except Exception as e:
            raise Exception(f"Error counting images: {str(e)}")

    async def delete_image(self, image_id: str):
        """ удаление изображения по _id"""
        result = await self.collection.delete_one({"_id": ObjectId(image_id)})
        return result.deleted_count > 0

# ------------thumbnail repo


class ThumbnailImageRepository:
    def __init__(self, database: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = database
        self.collection = self.db["images"]
        self._indexes_created = False
        self.thumbnail_size = (300, 300)  # Размер thumbnail'а

    async def ensure_indexes(self):
        if not self._indexes_created:
            await self.collection.create_index([("_id", 1)])
            await self.collection.create_index([("filename", 1)], unique=True)
            await self.collection.create_index([("created_at", -1), ("_id", 1)])
            print("Thumbnail image repository indexes ensured")
            self._indexes_created = True

    def _create_thumbnail_png(self, image_content: bytes) -> bytes:
        """Создает thumbnail в формате PNG с сохранением прозрачности"""
        try:
            # Открываем изображение из bytes
            image = Image.open(io.BytesIO(image_content))

            # Сохраняем оригинальный режим (для прозрачности)
            original_mode = image.mode

            # Создаем thumbnail с сохранением пропорций
            image.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)

            # Сохраняем в PNG с оптимизацией
            output = io.BytesIO()

            # Сохраняем с оптимизацией для PNG
            if original_mode in ('RGBA', 'LA', 'P'):
                # Сохраняем прозрачность для PNG
                image.save(output, format='PNG', optimize=True)
            else:
                # Для RGB и других режимов
                image.save(output, format='PNG', optimize=True)

            return output.getvalue()
        except Exception as e:
            print(f"Thumbnail creation error: {e}")
            return None

    async def create_image(self, filename: str, content: bytes, content_type: str, description: str) -> Dict[str, Any]:
        await self.ensure_indexes()

        # Создаем thumbnail
        thumbnail_content = self._create_thumbnail_png(content)

        document = {"filename": filename,
                    "content": Binary(content),  # BinData для MongoDB
                    "thumbnail": Binary(thumbnail_content)
                    if thumbnail_content else None,
                    "description": description,
                    "created_at": datetime.now(timezone.utc), "size": len(content),
                    "thumbnail_size": len(thumbnail_content)
                    if thumbnail_content else 0,
                    "content_type": content_type,
                    "thumbnail_type": "image/png" if thumbnail_content else None,
                    "has_thumbnail": thumbnail_content is not None}

        result = await self.collection.insert_one(document)
        return {"id": str(result.inserted_id), "has_thumbnail": thumbnail_content is not None}

    async def get_image(self, image_id: str, include_content: bool = True) -> Optional[dict]:
        """Получить полноразмерное изображение"""
        await self.ensure_indexes()
        try:
            projection = {"filename": 1, "description": 1,
                          "created_at": 1, "size": 1,
                          "content_type": 1,
                          "thumbnail_size": 1, "has_thumbnail": 1,
                          "thumbnail_type": 1}

            if include_content:
                projection["content"] = 1

            result = await self.collection.find_one(
                {"_id": ObjectId(image_id)}, projection
            )
            if result and "content" in result:
                # Конвертируем Binary обратно в bytes
                result["content"] = result["content"]

            return result
        except Exception as e:
            print(f"Error getting image by ID {image_id}: {e}")
            return None

    async def get_thumbnail(self, image_id: str) -> Optional[dict]:
        """Получить только thumbnail"""
        await self.ensure_indexes()
        try:
            result = await self.collection.find_one(
                {"_id": ObjectId(image_id)}, {"thumbnail": 1, "filename": 1, "thumbnail_type": 1}
            )

            if result and "thumbnail" in result:
                # Конвертируем Binary обратно в bytes
                result["thumbnail"] = result["thumbnail"]

            return result
        except Exception as e:
            print(f"Error getting thumbnail {image_id}: {e}")
            return None

    async def get_thumbnail_by_filename(self, filename: str) -> Optional[dict]:
        """Получить thumbnail по имени файла"""
        await self.ensure_indexes()
        try:
            result = await self.collection.find_one(
                {"filename": filename}, {"thumbnail": 1, "filename": 1, "thumbnail_type": 1}
            )

            if result and "thumbnail" in result:
                result["thumbnail"] = result["thumbnail"]

            return result
        except Exception as e:
            print(f"Error getting thumbnail by filename {filename}: {e}")
            return None

    async def get_images_after_date(
        self, after_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        """Получить список изображений (без content, только метаданные)"""
        await self.ensure_indexes()
        try:
            cursor = (self.collection.find(
                {"created_at": {"$gt": after_date}},
                {"content": 0,  # Исключаем основной контент
                    "thumbnail": 0}).sort("created_at", -1).skip(skip).limit(limit))

            images = []
            async for image in cursor:
                image["_id"] = str(image["_id"])
                images.append(image)
            return images
        except Exception as e:
            print(f"Error getting images after date: {e}")
            return []

    async def get_image_by_filename(self, filename: str, include_content: bool = True) -> Optional[dict]:
        await self.ensure_indexes()
        projection = {"filename": 1, "description": 1, "created_at": 1, "size": 1, "content_type": 1,
                      "thumbnail_size": 1, "has_thumbnail": 1, "thumbnail_type": 1}
        if include_content:
            projection["content"] = 1

        result = await self.collection.find_one({"filename": filename}, projection)

        if result and "content" in result:
            result["content"] = result["content"]

        return result

    async def count_images_after_date(self, after_date: datetime) -> int:
        await self.ensure_indexes()
        query = {"created_at": {"$gt": after_date}}
        return await self.collection.count_documents(query)

    async def delete_image(self, image_id: str) -> bool:
        result = await self.collection.delete_one({"_id": ObjectId(image_id)})
        return result.deleted_count > 0

    # Методы для миграции
    async def get_all_images_without_thumbnail(self) -> List[dict]:
        """Получить все изображения без thumbnail'ов"""
        cursor = self.collection.find(
            {"has_thumbnail": {"$ne": True}}, {"content": 1, "filename": 1, "content_type": 1}
        )

        images = []
        async for image in cursor:
            if "content" in image:
                image["content"] = image["content"]
                image["_id"] = str(image["_id"])
                images.append(image)
        return images

    async def update_image_with_thumbnail(self, image_id: str, thumbnail_content: bytes) -> bool:
        """Обновить изображение, добавив thumbnail"""
        try:
            result = await self.collection.update_one(
                {"_id": ObjectId(image_id)}, {
                    "$set": {"thumbnail": Binary(thumbnail_content), "thumbnail_size": len(thumbnail_content),
                             "thumbnail_type": "image/png", "has_thumbnail": True}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating image {image_id}: {e}")
            return False
