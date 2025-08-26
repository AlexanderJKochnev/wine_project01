# app/support/food/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class FoodShort(ShortSchema):
    pass


class FoodRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class FoodUpdate(UpdateSchema, CustomUpdSchema):
    pass


class FoodFull(FullSchema, CustomSchema):
    pass
