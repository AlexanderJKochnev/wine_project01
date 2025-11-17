# app/support/parser/schemas.py
from typing import Optional

from app.core.schemas.base import BaseModel
# from app.core.schemas.image_mixin import ImageUrlMixin


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


class CodeCreateRelation(BaseModel):
    code: str
    url: str
    status: StatusCreateRelation


class CodeCreateResponseSchema(CodeCreate):
    id: int


class CodeUpdate(BaseModel):
    code: Optional[str] = None
    url: Optional[str] = None
    status_id: Optional[int] = 1


class CodeRead(BaseModel):
    id: int
    code: str
    url: Optional[str] = None
    status: Optional[StatusReadRelation] = None


class CodeReadRelation(BaseModel):
    id: int
    code: str
    url: Optional[str] = None


class NameCreate(BaseModel):
    name: str
    url: str
    code_id: int
    status_id: Optional[int] = 1


class NameCreateRelation(BaseModel):
    name: str
    url: str
    code: CodeCreateRelation
    status: StatusCreateRelation


class NameCreateResponseSchema(NameCreate):
    id: int


class NameUpdate(BaseModel):
    name: Optional[str] = None
    code_id: Optional[int] = None
    url: Optional[str] = None
    status_id: Optional[int] = 1


class NameRead(BaseModel):
    id: int
    name: str
    code: Optional[CodeReadRelation]
    url: Optional[str] = None
    status: Optional[StatusReadRelation] = None


class NameReadRelation:
    id: int
    name: str
    url: Optional[str] = None


class RawdataCreate(BaseModel):
    body_html: str
    name_id: int
    status_id: Optional[int] = 1


class RawdataCreateRelation(BaseModel):
    body_html: str
    name: NameCreateRelation
    status: StatusCreateRelation


class RawdataCreateResponseSchema(RawdataCreate):
    id: int


class RawdataUpdate(BaseModel):
    body_html: Optional[str] = None
    name_id: Optional[int] = None
    status_id: Optional[int] = 1


class RawdataRead(BaseModel):
    id: int
    body_html: Optional[str]
    name_id: int
    status: Optional[StatusRead] = None


class ImageCreate(BaseModel):
    name_id: int
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class ImageCreateRelation(BaseModel):
    image_path: Optional[str] = None
    image_id: Optional[str] = None
    name: NameCreateRelation


class ImageCreateResponseSchema(ImageCreate):
    id: int


class ImageUpdate(BaseModel):
    image_path: Optional[str] = None
    image_id: Optional[str] = None
    name_id: Optional[int] = None


class ImageRead(BaseModel):
    id: int
    name_id: int  # NameReadRelation
    image_path: Optional[str] = None
    image_id: Optional[str] = None
