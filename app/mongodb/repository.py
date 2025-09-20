# app/mongodb/repository.py
from datetime import datetime

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFSBucket

from app.mongodb.config import get_mongo_db  # NOQA: F401
from app.mongodb.models import DocumentResponse, ImageResponse


class MongoDBRepository:
    def __init__(self, db):
        self.db = db
        self.fs_images = AsyncIOMotorGridFSBucket(self.db, bucket_name="images")
        self.fs_docs = AsyncIOMotorGridFSBucket(self.db, bucket_name="documents")

    async def save_image(self, image_data: dict) -> str:
        image_data["upload_date"] = datetime.utcnow()
        file_id = await self.fs_images.upload_from_stream(
            image_data["filename"],
            image_data["content"],
            metadata={
                "description": image_data.get("description"),
                "owner_id": image_data["owner_id"],
                "size": len(image_data["content"])
            }
        )
        return str(file_id)

    async def get_image(self, file_id: str) -> dict:
        file = await self.fs_images.open_download_stream(ObjectId(file_id))
        content = await file.read()
        return {
            "filename": file.filename,
            "content": content,
            "metadata": file.metadata
        }

    async def delete_image(self, file_id: str) -> bool:
        try:
            await self.fs_images.delete(ObjectId(file_id))
            return True
        except Exception:
            return False

    async def save_document(self, doc_data: dict) -> str:
        doc_data["upload_date"] = datetime.utcnow()
        file_id = await self.fs_docs.upload_from_stream(
            doc_data["filename"],
            doc_data["content"],
            metadata={
                "description": doc_data.get("description"),
                "owner_id": doc_data["owner_id"],
                "size": len(doc_data["content"])
            }
        )
        return str(file_id)

    async def get_document(self, file_id: str) -> dict:
        file = await self.fs_docs.open_download_stream(ObjectId(file_id))
        content = await file.read()
        return {
            "filename": file.filename,
            "content": content,
            "metadata": file.metadata
        }

    async def delete_document(self, file_id: str) -> bool:
        try:
            await self.fs_docs.delete(ObjectId(file_id))
            return True
        except Exception:
            return False

    async def get_user_images(self, owner_id: int):
        cursor = self.fs_images.find({"metadata.owner_id": owner_id})
        images = []
        async for file in cursor:
            images.append(ImageResponse(
                _id=file._id,
                filename=file.filename,
                description=file.metadata.get("description"),
                owner_id=file.metadata["owner_id"],
                created_at=file.upload_date,
                size=file.metadata["size"]
            ))
        return images

    async def get_user_documents(self, owner_id: int):
        cursor = self.fs_docs.find({"metadata.owner_id": owner_id})
        docs = []
        async for file in cursor:
            docs.append(DocumentResponse(
                _id=file._id,
                filename=file.filename,
                description=file.metadata.get("description"),
                owner_id=file.metadata["owner_id"],
                created_at=file.upload_date,
                size=file.metadata["size"]
            ))
        return docs
