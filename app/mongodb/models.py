# app/mongodb/models.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type, _handler):
        return {'type': 'str', 'json_schema': {'type': 'string', 'pattern': '^[0-9a-fA-F]{24}$'}}

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)


class ImageBase(BaseModel):
    filename: str
    description: Optional[str] = None
    owner_id: int  # ID из PostgreSQL


class ImageCreate(ImageBase):
    content: bytes  # Бинарные данные изображения


class ImageResponse(ImageBase):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime
    size: int

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class DocumentBase(BaseModel):
    filename: str
    description: Optional[str] = None
    owner_id: int  # ID из PostgreSQL


class DocumentCreate(DocumentBase):
    content: bytes  # Бинарные данные документа


class DocumentResponse(DocumentBase):
    id: PyObjectId = Field(alias="_id")
    created_at: datetime
    size: int

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
