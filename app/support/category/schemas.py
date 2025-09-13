# app/support/category/schemas.py

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


class CategoryRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CategoryCreateResponseSchema(CategoryCreate, CreateResponse):
    pass
