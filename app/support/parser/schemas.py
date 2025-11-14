# app/support/parser/schemas.py
from typing import Optional

from app.core.schemas.base import BaseModel


class StatusCreate(BaseModel):
    status: str


class StatusCreateRelation(BaseModel):
    status: str


class StatusCreateResponseSchema(StatusCreate):
    id: int


class StatusUpdate(BaseModel):
    status: Optional[str] = None


class StatusRead(BaseModel):
    id: int
    status: str


class StatusReadRelation(BaseModel):
    id: int
    status: str


class CodeCreate(BaseModel):
    code: str
    url: str
    status_id: Optional[int] = 1


class CodeCreateResponseSchema(CodeCreate):
    id: int


class CodeUpdate(BaseModel):
    code: Optional[str] = None
    url: Optional[str] = None
    status_id: Optional[int] = 1


class CodeRead(BaseModel):
    code: str
    url: Optional[str] = None
    status: Optional[StatusRead] = None


class NameCreate(BaseModel):
    name: str
    url: str
    code_id: int
    status_id: Optional[int] = 1


class NameCreateResponseSchema(NameCreate):
    id: int


class NameUpdate(BaseModel):
    name: Optional[str] = None
    code_id: Optional[int] = None
    url: Optional[str] = None
    status_id: Optional[int] = 1


class NameRead(BaseModel):
    name: str
    code: CodeRead
    url: Optional[str] = None
    status: Optional[StatusRead] = None


class RawdataCreate(BaseModel):
    body_html: str
    name_id: int
    status_id: Optional[int] = 1


class RawdataCreateResponseSchema(RawdataCreate):
    id: int


class RawdataUpdate(BaseModel):
    body_html: Optional[str] = None
    name_id: Optional[int] = None
    status_id: Optional[int] = 1


class RawdataRead(BaseModel):
    body_html: str
    name: NameRead
    status: Optional[StatusRead] = None


class ImageCreate(BaseModel):
    name_id: int
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class ImageCreateResponseSchema(ImageCreate):
    id: int


class ImageUpdate(BaseModel):
    image_path: Optional[str] = None
    image_id: Optional[str] = None
    name_id: Optional[int] = None


class ImageRead(BaseModel):
    image_path: Optional[str] = None
    image_id: Optional[str] = None
    name: NameRead
