# app/mongodb/repository.py
from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
# from app.mongodb.config import get_mongo_db
from app.mongodb.models import FileResponse


class MongoDBRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.images_collection = self.db["images"]
        self.documents_collection = self.db["documents"]

    async def save_file(self, collection, file_data: dict) -> str:
        file_data["created_at"] = datetime.utcnow()
        file_data["size"] = len(file_data["content"])
        result = await collection.insert_one(file_data)
        return str(result.inserted_id)

    async def get_file(self, collection, file_id: str) -> dict:
        file = await collection.find_one({"_id": ObjectId(file_id)})
        if file:
            file["_id"] = str(file["_id"])
        return file

    async def delete_file(self, collection, file_id: str) -> bool:
        result = await collection.delete_one({"_id": ObjectId(file_id)})
        return result.deleted_count > 0

    async def get_user_files(self, collection, owner_id: int):
        files = []
        async for file in collection.find({"owner_id": owner_id}):
            file["_id"] = str(file["_id"])
            files.append(FileResponse(**file))
        return files

    # Методы для изображений
    async def save_image(self, image_data: dict) -> str:
        return await self.save_file(self.images_collection, image_data)

    async def get_image(self, file_id: str) -> dict:
        return await self.get_file(self.images_collection, file_id)

    async def delete_image(self, file_id: str) -> bool:
        return await self.delete_file(self.images_collection, file_id)

    async def get_user_images(self, owner_id: int):
        return await self.get_user_files(self.images_collection, owner_id)

    # Методы для документов
    async def save_document(self, doc_data: dict) -> str:
        return await self.save_file(self.documents_collection, doc_data)

    async def get_document(self, file_id: str) -> dict:
        return await self.get_file(self.documents_collection, file_id)

    async def delete_document(self, file_id: str) -> bool:
        return await self.delete_file(self.documents_collection, file_id)

    async def get_user_documents(self, owner_id: int):
        return await self.get_user_files(self.documents_collection, owner_id)
