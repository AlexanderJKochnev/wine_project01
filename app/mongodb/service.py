# app/mongodb/service.py
from app.mongodb.config import get_mongo_db
from app.mongodb.repository import MongoDBRepository
from app.mongodb.models import ImageCreate, DocumentCreate
from fastapi import HTTPException, status, Depends


class MongoDBService:
    def __init__(self, db):
        self.repository = MongoDBRepository(db)
    
    async def create_image(self, image: ImageCreate, owner_id: int) -> str:
        image_data = {"filename": image.filename, "description": image.description, "owner_id": owner_id,
                "content": image.content, "content_type": "image"}
        return await self.repository.save_image(image_data)
    
    async def get_image(self, file_id: str, owner_id: int) -> dict:
        image_data = await self.repository.get_image(file_id)
        if not image_data:
            raise HTTPException(status_code = 404, detail = "Image not found")
        if image_data["owner_id"] != owner_id:
            raise HTTPException(status_code = 403, detail = "Access denied")
        return image_data
    
    async def delete_image(self, file_id: str, owner_id: int) -> bool:
        # Проверяем ownership перед удалением
        image_data = await self.repository.get_image(file_id)
        if not image_data:
            raise HTTPException(status_code = 404, detail = "Image not found")
        if image_data["owner_id"] != owner_id:
            raise HTTPException(status_code = 403, detail = "Access denied")
        
        return await self.repository.delete_image(file_id)
    
    async def create_document(self, document: DocumentCreate, owner_id: int) -> str:
        doc_data = {"filename": document.filename, "description": document.description, "owner_id": owner_id,
                "content": document.content, "content_type": "document"}
        return await self.repository.save_document(doc_data)
    
    async def get_document(self, file_id: str, owner_id: int) -> dict:
        doc_data = await self.repository.get_document(file_id)
        if not doc_data:
            raise HTTPException(status_code = 404, detail = "Document not found")
        if doc_data["owner_id"] != owner_id:
            raise HTTPException(status_code = 403, detail = "Access denied")
        return doc_data
    
    async def delete_document(self, file_id: str, owner_id: int) -> bool:
        doc_data = await self.repository.get_document(file_id)
        if not doc_data:
            raise HTTPException(status_code = 404, detail = "Document not found")
        if doc_data["owner_id"] != owner_id:
            raise HTTPException(status_code = 403, detail = "Access denied")
        
        return await self.repository.delete_document(file_id)
    
    async def get_user_images_list(self, owner_id: int):
        return await self.repository.get_user_images(owner_id)
    
    async def get_user_documents_list(self, owner_id: int):
        return await self.repository.get_user_documents(owner_id)


# Фабрика сервиса
async def get_mongo_service(db=Depends(get_mongo_db)):
    return MongoDBService(db)