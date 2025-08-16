# app/support/drink/schemas.py

from pydantic import BaseModel


class FileBase(BaseModel):
    filename: str
    content_type: str
    size: int
    seaweedfs_id: str


class FileCreate(FileBase):
    pass


class FileRead(FileBase):
    id: int


class FileUpdate(BaseModel):
    filename: str | None = None
    # Другие метаданные, если нужно
