# app/mongodb/models.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FileBase(BaseModel):
    filename: str
    description: Optional[str] = None
    drink_id: int


class ImageCreate(FileBase):
    content: bytes


class DocumentCreate(FileBase):
    content: bytes


class FileResponse(FileBase):
    id: str = Field(alias="_id")
    created_at: datetime
    size: int
    content_type: str
