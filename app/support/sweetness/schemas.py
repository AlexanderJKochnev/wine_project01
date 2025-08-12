# app/support/sweetness/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.category.schemas import CategoryShort
from pydantic import ConfigDict


class SweetnessCustom:
    category_id: int


class SweetnessShort(ShortSchema):
    pass


class SweetnessRead(BaseSchema):
    pass


class SweetnessCreate(BaseSchema, SweetnessCustom):
    pass


class SweetnessUpdate(UpdateSchema, SweetnessCustom):
    pass


class SweetnessFull(FullSchema, SweetnessCustom):
    pass
