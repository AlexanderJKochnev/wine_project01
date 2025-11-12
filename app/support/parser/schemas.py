# app/support/parser/schemas.py
from typing import Optional

from pydantic import computed_field, Field

from app.core.schemas.base import PkSchema, DateSchema


class StatusCreateSchema(DateSchema):
    status: str


class StatusUpdateSchema(DateSchema):
    status: Optional[str] = None


class StatusReadSchema(DateSchema):
    id: int
    status: str


class CodeCreateSchema(DateSchema):
    code: str
    url: Optional[str] = None
    status_id: Optional[str] = 1


class CodeUpdateSchema(DateSchema):
    code: Optional[str] = None
    url: Optional[str] = None
    status_id: Optional[str] = None


class CodeReadSchema(DateSchema):
    code: str
    url: Optional[str] = None
    status: Optional[StatusReadSchema] = None


class NameCreateSchema(DateSchema):
    name: str
    url: Optional[str] = None
    code_id: int
    status_id: Optional[str] = 1


class NameUpdateSchema(DateSchema):
    name: Optional[str] = None
    code_id = Optional[int] = None
    url: Optional[str] = None
    status_id: Optional[str] = None


class NameReadSchema(DateSchema):
    name: str
    code: CodeReadSchema
    url: Optional[str] = None
    status: Optional[StatusReadSchema] = None


class RawdataCreateSchema(DateSchema):
    body_html: str
    name_id: int
    status_id: Optional[str] = 1


class RawdataUpdateSchema(DateSchema):
    body_html: Optional[str] = None
    name_id = Optional[int] = None
    status_id: Optional[str] = None


class RawdataReadSchema(DateSchema):
    body_html: str
    name: NameReadSchema
    status: Optional[StatusReadSchema] = None


class ImageCreateSchema(DateSchema):
    file_id: Optional[str] = None
    file_url: Optional[str] = None
    url: Optional[str] = None
    name_id: int
    status_id: Optional[str] = 1


class ImageUpdateSchema(DateSchema):
    file_id: Optional[str] = None
    file_url: Optional[str] = None
    url: Optional[str] = None
    status_id: Optional[str] = None


class ImageReadSchema(DateSchema):
    file_id: Optional[str] = None
    file_url: Optional[str] = None
    name: NameReadSchema
    status: Optional[StatusReadSchema] = None
