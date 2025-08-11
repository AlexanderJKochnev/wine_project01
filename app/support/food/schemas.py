# app/support/food/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from pydantic import ConfigDict


class FoodCustom:
    pass


class FoodShort(ShortSchema):
    pass


class FoodRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class FoodCreate(BaseSchema, FoodCustom):
    pass


class FoodUpdate(UpdateSchema, FoodCustom):
    pass


class FoodFull(FullSchema, FoodCustom):
    pass
