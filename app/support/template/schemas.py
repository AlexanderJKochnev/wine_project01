# app/support/template/schemas.py

from app.core.schemas.base_schema import BaseModel


class TemplateBase(BaseModel):
    """ список полей модели """
    name: str


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(TemplateBase):
    pass


class TemplateResponse(TemplateBase):
    id: int


class TemplateListResponse(TemplateBase):
    id: int | None = None
    name: str | None = None
