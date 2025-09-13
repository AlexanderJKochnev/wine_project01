# app/support/food/schemas.py

from pydantic import ConfigDict
from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema, CreateResponse)


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomCreateRelation:
    pass


class CustomUpdSchema:
    pass


class FoodRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreateResponseSchema(FoodCreate, CreateResponse):
    pass
