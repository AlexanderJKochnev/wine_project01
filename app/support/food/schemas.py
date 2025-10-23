# app/support/food/schemas.py

from pydantic import ConfigDict
from typing import Optional
from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema, CreateResponse)
from app.support.superfood.schemas import SuperfoodRead, SuperfoodCreateRelation


class CustomReadSchema:
    superfood: SuperfoodRead


class CustomCreateSchema:
    superfood_id: int


class CustomCreateRelation:
    superfood: SuperfoodCreateRelation


class CustomUpdSchema:
    superfood: Optional[SuperfoodCreateRelation]


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
