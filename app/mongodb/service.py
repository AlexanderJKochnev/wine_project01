# app/mongodb/service.py
from typing import List
import io
from fastapi import Depends, HTTPException, status
from PIL import Image
from app.mongodb.repository import DocumentRepository, ImageRepository
from app.mongodb.config import settings
from app.mongodb.utils import (make_transparent_white_bg, file_name, image_aligning,
                               remove_background, remove_background_with_mask)


class ImageService:
    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository


    async def upload_image(self, filename: str, content: bytes, description: str, drink_id: int):
        try:
            pass
            # content = image_aligning(content)
        except Exception:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = "image aligning fault"
                    )
        try:
            pass
            # content = remove_background_with_mask(content)
        except Exception:
            raise HTTPException(
                    status_code = status.HTTP_400_BAD_REQUEST, detail = "remove background fault"
                    )
        print(f'{content=}============================')
        if len(content) > 8 * 1024 * 1024:
            # сюда вставить обработку изображения
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        filename=file_name(filename, settings.LENGTH_RANDOM_NAME, '.png')
        return await self.image_repository.create_image(filename, content, description, drink_id)

    async def get_image(self, image_id: str, drink_id: int):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        if image["drink_id"] != drink_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return image

    async def get_user_images(self, drink_id: int) -> List[dict]:
        return await self.image_repository.get_user_images(drink_id)

    async def delete_image(self, image_id: str, drink_id: int):
        image = await self.image_repository.get_image(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
        if image["drink_id"] != drink_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.image_repository.delete_image(image_id)


class DocumentService:
    def __init__(self, document_repository: DocumentRepository = Depends()):
        self.document_repository = document_repository

    async def upload_document(self, filename: str, content: bytes, description: str, drink_id: int):
        if len(content) > 8 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
        return await self.document_repository.create_document(filename, content, description, drink_id)

    async def get_document(self, document_id: str, drink_id: int):
        document = await self.document_repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if document["drink_id"] != drink_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return document

    async def get_user_documents(self, drink_id: int) -> List[dict]:
        return await self.document_repository.get_user_documents(drink_id)

    async def delete_document(self, document_id: str, drink_id: int):
        document = await self.document_repository.get_document(document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        if document["drink_id"] != drink_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return await self.document_repository.delete_document(document_id)
