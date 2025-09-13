# app/support/food/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomCreateRelation:
    pass


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class FoodRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
