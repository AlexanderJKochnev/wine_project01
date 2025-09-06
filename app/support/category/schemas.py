# app/support/category/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomReadSchema:
    """ кастомные поля """
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class CategoryRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
