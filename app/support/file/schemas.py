# app/support/file/schemas.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional
from app.core.models.mongo_mixin import MongoRef


class ImageBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None


class ImageCreate(ImageBase):
    pass


class ImageUpdate(ImageBase):
    pass


class ImageInDB(ImageBase):
    id: int
    mongo_ref: Optional[MongoRef] = None
    uploaded_by: int
    created_at: datetime
    url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class ImageResponse(ImageInDB):
    pass

# Аналогично для Document...


class DocumentBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    alt_text: Optional[str] = None


class DocumentCreate(ImageBase):
    pass


class DocumentUpdate(ImageBase):
    pass


class DocumentInDB(ImageBase):
    id: int
    mongo_ref: Optional[MongoRef] = None
    uploaded_by: int
    created_at: datetime
    url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class DocumentResponse(ImageInDB):
    pass
