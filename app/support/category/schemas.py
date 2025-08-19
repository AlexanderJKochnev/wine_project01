# app/support/category/schemas.py
from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema


class CategoryCustom:
    pass


class CategoryShort(ShortSchema):
    pass


class CategoryRead(BaseSchema, CategoryCustom):
    pass
    # count_drink: Optional[int] = 0


class CategoryCreate(BaseSchema):
    pass


class CategoryUpdate(UpdateSchema):
    pass


class CategoryFull(FullSchema, CategoryRead, CategoryCustom):
    pass
