# app/support/file/router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config.database.db_async import get_db
from app.core.services.mongo_service import image_service
# from app.support.file.service import FileService
# from app.support.file.schemas import ImageResponse
from app.core.security import get_current_active_user
from app.auth.models import User
from app.core.config.database.db_amongo import get_mongodb

router = APIRouter(prefix="/images", tags=["images"])


@router.get("/ping")
async def ping_db(db: AsyncIOMotorDatabase = Depends(get_mongodb)):
    """Проверка подключения к MongoDB"""
    try:
        await db.command("ping")
        return {'status': 'ok', 'database': db.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot connect to DB: {e}")

"""
@router.post("/", response_model=ImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(file: UploadFile = File(...),
                       db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_active_user),
                       file_service: FileService = Depends()):
    # Загрузка изображения

    return await file_service.upload_image(db=db,
                                           file=file,
                                           uploader_id=current_user.id)
"""

@router.get("/files/{file_id}")
async def get_file(file_id: str,
                   current_user: User = Depends(get_current_active_user)):
    """
    Получение файла из MongoDB
    """
    pass
    # document = await image_service.get_document(file_id)
    # if not document:
    #    raise HTTPException(status_code=404, detail="File not found")

    # Проверка прав доступа может быть добавлена здесь
"""
    return {"filename": document["filename"],
            "content_type": document["content_type"],
            "data": document["data"],
            "url": document["url"]}
"""
