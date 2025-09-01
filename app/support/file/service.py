# app/support/file/service.py
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.support.file.model import Image
from app.support.file.schemas import ImageCreate
from app.core.services.mongo_service import image_service
from app.crud.crud_image import image_crud
from typing import Optional


class FileService:
    async def upload_image(self, db: AsyncSession,
                           file: UploadFile, uploader_id: int,
                           title: Optional[str] = None) -> Image:
        # Проверяем тип файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Only image files are allowed"
            )

        # Читаем файл
        file_data = await file.read()

        # Сохраняем в MongoDB
        mongo_id = await image_service.save_document(file_data=file_data,
                                                     filename=file.filename,
                                                     content_type=file.content_type,
                                                     metadata={"uploader_id": uploader_id})

        # Сохраняем метаданные в PostgreSQL
        image_in = ImageCreate(title=title or file.filename,
                               alt_text=title or file.filename)

        image_obj = await image_crud.create(db, obj_in=image_in)
        image_obj.set_mongo_ref(mongo_id)
        image_obj.uploaded_by = uploader_id

        await db.commit()
        await db.refresh(image_obj)

        return image_obj
