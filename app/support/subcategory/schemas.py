# app/support/subcategory/schemas.py

from pydantic import ConfigDict
from typing import Optional
from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema, CreateResponse)
from app.support.category.schemas import CategoryCreateRelation, CategoryRead


class CustomReadSchema:
    category: CategoryRead


class CustomCreateSchema:
    category_id: int


class CustomCreateRelation:
    category: CategoryCreateRelation


class CustomUpdSchema:
    category: Optional[CategoryCreateRelation]


class SubcategoryRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryCreateResponseSchema(SubcategoryCreate, CreateResponse):
    pass
