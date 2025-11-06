# app/mongodb/repository.py
from bson import ObjectId
from datetime import datetime, timezone
from fastapi import Depends
from typing import List, Tuple, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.mongodb.config import get_database
# from app.mongodb.models import FileResponse


class ImageRepository:
    def __init__(self, database: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = database
        self.collection = self.db["images"]
        self._indexes_created = False

    async def ensure_indexes(self):
        """Создает индексы при первом использовании репозитория"""
        if not self._indexes_created:
            try:
                await self.collection.create_index([("_id", 1)])
                await self.collection.create_index([("filename", -1)], unique=True)
                await self.collection.create_index([("created_at", -1), ("_id", 1)])
                # await self.collection.create_index([("filename", "text")])  # Текстовый поиск
                print("Optimized image repository indexes ensured")
                self._indexes_created = True
            except Exception as e:
                print(f"Index creation error: {e}")

    async def create_image(self, filename: str, content: bytes, content_type: str, description: str) -> str:
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
        # await self.ensure_indexes()
        # return await self.collection.find_one({"_id": ObjectId(image_id)})
        await self.ensure_indexes()
        try:
            # Используем projection чтобы не получать content если не нужно
            return await self.collection.find_one(
                {"_id": ObjectId(image_id)},
                {"content": 1, "filename": 1, "content_type": 1, "description": 1, "created_at": 1}
            )
        except Exception as e:
            print(f"Error getting image by ID {image_id}: {e}")
            return None

    async def get_image_by_filename(self, filename: str):
        # return await self.collection.find_one({"filename": filename})
        """Оптимизированное получение по filename"""
        await self.ensure_indexes()
        try:
            return await self.collection.find_one(
                {"filename": filename},
                {"content": 1, "filename": 1, "content_type": 1, "description": 1, "created_at": 1}
            )
        except Exception as e:
            print(f"Error getting image by filename {filename}: {e}")
            return None

    async def get_image_metadata_only(self, image_id: str) -> Optional[dict]:
        """Только метаданные (без content) - для списков"""
        await self.ensure_indexes()
        try:
            return await self.collection.find_one(
                {"_id": ObjectId(image_id)}, {"content": 0}  # Исключаем content
            )
        except Exception as e:
            print(f"Error getting image metadata {image_id}: {e}")
            return None

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
        result = await self.collection.delete_one({"_id": ObjectId(image_id)})
        return result.deleted_count > 0

    async def get_images_after_date(
        self, after_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[dict]:
        """Оптимизированный пагинированный запрос"""
        await self.ensure_indexes()
        try:
            # Исключаем content из результатов - только метаданные
            cursor = self.collection.find(
                {"created_at": {"$gt": after_date}}, {"content": 0}  # Не получаем бинарные данные в списках!
            ).sort("created_at", -1).skip(skip).limit(limit)

            images = []
            async for image in cursor:
                image["_id"] = str(image["_id"])
                images.append(image)
            return images
        except Exception as e:
            print(f"Error getting images after date: {e}")
            return []

    async def get_images_after_date_nopage(self, after_date: datetime) -> List[Tuple]:
        """Оптимизированный запрос без пагинации"""
        await self.ensure_indexes()
        try:
            # Только нужные поля
            cursor = self.collection.find(
                {"created_at": {"$gt": after_date}}, {"filename": 1, "_id": 1}  # Только эти поля
            ).sort("created_at", -1)

            images = []
            async for image in cursor:
                images.append((image['filename'], str(image["_id"])))
            return images
        except Exception as e:
            print(f"Error getting images nopage: {e}")
            return []
