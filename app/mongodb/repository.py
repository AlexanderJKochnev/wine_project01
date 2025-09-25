# app/mongodb/repository.py
from bson import ObjectId
from datetime import datetime
from fastapi import Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.mongodb.config import get_database
from app.mongodb.models import FileResponse


class ImageRepository:
    def __init__(self, database: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = database
        self.collection = self.db["images"]

    async def create_image(self, filename: str, content: bytes, content_type: str, description: str) -> str:
        document = {
            "filename": filename,
            "content": content,
            "description": description,
            "created_at": datetime.utcnow(),
            "size": len(content),
            "content_type": content_type
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_image(self, image_id: str):
        return await self.collection.find_one({"_id": ObjectId(image_id)})


    async def get_images_after_date(self,
                             after_date: datetime,
                             skip: int = 0,
                             limit: int = 100) -> List[FileResponse]:
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
        result = await self.collection.delete_one({"_id": ObjectId(image_id)})
        return result.deleted_count > 0


