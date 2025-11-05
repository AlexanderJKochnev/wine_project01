# app/mongodb/models.py
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional, List
from app.core.config.project_config import settings

from bson import ObjectId


class ZeroBase(BaseModel):
    filename: str = Field(default=None, exclude=True)

    @computed_field
    @property
    def image_url(self) -> Optional[str]:
        """
        Генерирует полный URL изображения на основе image_path и BASE_URL из настроек.
        Если image_path пустой — возвращает None.
        http://83.167.126.4:18091/mongodb/images/68d6ead9da55b293d13a0f5d
        """
        try:
            if not self.filename:
                return None
            base_url = settings.BASE_URL or 'http://localhost/'
            prefix = settings.MONGODB_PREFIX or 'mongodb'
            images = settings.FILES_PREFIX or 'images'
            url = f"{base_url.rstrip('/')}/{prefix.strip('/')}/{images.strip('/')}/{self.filename.strip('/')}"
            return url
        except Exception as e:
            print(f'image_url.error: {e}')
            return None


class NoPathBase(BaseModel):
    filename: str = Field(default=None, exclude=True)


class FileBase(NoPathBase):
    # если нужно что бы возвращался путь к файлу замени NoPathBase на ZeroBase
    description: Optional[str] = None


class ImageCreate(FileBase):
    content: bytes


class FileResponse(FileBase):
    id: str = Field(alias="_id")
    filename: str
    created_at: datetime
    size: int
    content_type: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: lambda v: str(v)
        }


class FileListResponse(BaseModel):
    """Модель ответа со списком изображений"""
    images: List[FileResponse]
    total: int
    has_more: bool


class JustListResponse(ZeroBase):
    images: List[FileResponse]
