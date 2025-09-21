# app/mongodb/repository.py
from bson import ObjectId
from datetime import datetime
from fastapi import Depends
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.mongodb.config import get_database
# from app.mongodb.models import FileResponse


class ImageRepository:
    def __init__(self, database: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = database
        self.collection = self.db["images"]

    async def create_image(self, filename: str, content: bytes, description: str, owner_id: int):
        document = {
            "filename": filename,
            "content": content,
            "description": description,
            "owner_id": owner_id,
            "created_at": datetime.utcnow(),
            "size": len(content)
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_image(self, image_id: str):
        return await self.collection.find_one({"_id": ObjectId(image_id)})

    async def get_user_images(self, owner_id: int) -> List[dict]:
        cursor = self.collection.find({"owner_id": owner_id})
        images = []
        async for image in cursor:
            image["_id"] = str(image["_id"])
            images.append(image)
        return images

    async def delete_image(self, image_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(image_id)})
        return result.deleted_count > 0


class DocumentRepository:
    def __init__(self, database: AsyncIOMotorDatabase = Depends(get_database)):
        self.db = database
        self.collection = self.db["documents"]

    async def create_document(self, filename: str, content: bytes, description: str, owner_id: int):
        document = {
            "filename": filename,
            "content": content,
            "description": description,
            "owner_id": owner_id,
            "created_at": datetime.utcnow(),
            "size": len(content)
        }
        result = await self.collection.insert_one(document)
        return str(result.inserted_id)

    async def get_document(self, document_id: str):
        return await self.collection.find_one({"_id": ObjectId(document_id)})

    async def get_user_documents(self, owner_id: int) -> List[dict]:
        cursor = self.collection.find({"owner_id": owner_id})
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(doc)
        return documents

    async def delete_document(self, document_id: str):
        result = await self.collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0
