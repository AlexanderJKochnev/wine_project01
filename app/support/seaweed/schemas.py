# app/support/drink/schemas.py

from pydantic import BaseModel

class FileCreate(BaseModel):
    filename: str
    content_type: str
    size: int

class FileResponse(FileCreate):
    id: int
    seaweedfs_id: str