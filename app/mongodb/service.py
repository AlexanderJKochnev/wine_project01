# app/mongodb/service.py
from typing import List
import io
from fastapi import Depends, HTTPException, status
from PIL import Image
from app.mongodb.repository import DocumentRepository, ImageRepository
from app.mongodb.config import settings


class ImageService:
    def __init__(self, image_repository: ImageRepository = Depends()):
        self.image_repository = image_repository

    def image_aligning(self, content):
        """ подгон изображения под требуемый разимер"""
        width = settings.IMAGE_WIDTH
        height = settings.IMAGE_HEIGH
        quality = settings.IMAGE_QUALITY
        try:
            # Открываем изображение
            image = Image.open(io.BytesIO(content))
            original_width, original_height = image.size
            original_ratio = original_width / original_height
            ratio = width / height
            if original_ratio > ratio:
                # height priority
                new_height = height
                new_width = int(original_width * (height / original_height))
            else:
                # width_priority
                new_width = width
                new_height = int(original_height * (width / original_width))
            resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            img_byte_arr = io.BytesIO()
            format = image.format if image.format else 'JPEG'
            resized_image.save(img_byte_arr, format = format, optimize = True)

            # Получаем обработанное содержимое
            new_content = img_byte_arr.getvalue()
            return new_content
        except Exception as e:
            return content
            raise HTTPException(status_code = 400, detail = f"Ошибка обработки изображения: {str(e)}")
            

    async def upload_image(self, filename: str, content: bytes, description: str, drink_id: int):
        content = self.image_aligning(content)
        if len(content) > 8 * 1024 * 1024:
            # сюда вставить обработку изображения
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File too large"
            )
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
