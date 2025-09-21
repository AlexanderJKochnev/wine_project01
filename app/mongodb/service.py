# app/mongodb/service.py
from app.mongodb.repository import ImageRepository, DocumentRepository
from fastapi import HTTPException, status, Depends
from typing import List


class ImageService:
    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository

    async def upload_image(self, filename: str, content: bytes, description: str, owner_id: int):
        if len(content) > 8 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        return await self.image_repository.create_image(filename, content, description, owner_id)

    async def get_image(self, image_id: str, owner_id: int):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        if image["owner_id"] != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return image

    async def get_user_images(self, owner_id: int) -> List[dict]:
        return await self.image_repository.get_user_images(owner_id)

    async def delete_image(self, image_id: str, owner_id: int):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        if image["owner_id"] != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.image_repository.delete_image(image_id)


class DocumentService:
    def __init__(self, document_repository: DocumentRepository = Depends()):
        self.document_repository = document_repository

    async def upload_document(self, filename: str, content: bytes, description: str, owner_id: int):
        if len(content) > 8 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        return await self.document_repository.create_document(filename, content, description, owner_id)

    async def get_document(self, document_id: str, owner_id: int):
        document = await self.document_repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if document["owner_id"] != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return document

    async def get_user_documents(self, owner_id: int) -> List[dict]:
        return await self.document_repository.get_user_documents(owner_id)

    async def delete_document(self, document_id: str, owner_id: int):
        document = await self.document_repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if document["owner_id"] != owner_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.document_repository.delete_document(document_id)
