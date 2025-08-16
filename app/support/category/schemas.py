# app/support/category/schemas.py
from typing import Optional
from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from pydantic import ConfigDict


class CategoryCustom:
    pass


class CategoryShort(ShortSchema):
    pass


class CategoryRead(BaseSchema, CategoryCustom):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    count_drink: Optional[int] = 0


class CategoryCreate(BaseSchema):
    pass


class CategoryUpdate(UpdateSchema):
    pass


class CategoryFull(FullSchema, CategoryRead, CategoryCustom):
    pass
