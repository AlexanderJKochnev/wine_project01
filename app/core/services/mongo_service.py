# app/core/services/mongo_service.py
from app.core.config.database.db_amongo import get_mongodb
from app.core.config.database.mongo_config import settings
from bson import ObjectId
from typing import Optional, Dict, Any
import datetime


class MongoService:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    async def save_document(
        self, file_data: bytes, filename: str, content_type: str, metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        db = get_mongodb()
        collection = db[self.collection_name]

        document = {"filename": filename,
                    "content_type": content_type,
                    "data": file_data,
                    "uploaded_at": datetime.datetime.utcnow(),
                    "metadata": metadata or {}}

        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def get_document(self, document_id: str) -> Optional[Dict]:
        db = get_mongodb()
        collection = db[self.collection_name]

        if not ObjectId.is_valid(document_id):
            return None

        document = await collection.find_one({"_id": ObjectId(document_id)})
        if document:
            document["_id"] = str(document["_id"])
            # Генерируем URL для доступа к документу
            document["url"] = f"{settings.SERVER_HOST}/api/v1/files/{document['_id']}"
        return document

    async def delete_document(self, document_id: str) -> bool:
        db = get_mongodb()
        collection = db[self.collection_name]

        if not ObjectId.is_valid(document_id):
            return False

        result = await collection.delete_one({"_id": ObjectId(document_id)})
        return result.deleted_count > 0


# Создаем экземпляры сервисов для разных типов файлов
image_service = MongoService("images")
document_service = MongoService("documents")
