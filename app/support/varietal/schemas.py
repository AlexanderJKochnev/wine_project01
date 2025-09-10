# app/support/varietal/schemas.py

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


class VarietalRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class VarietalCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class VarietalCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class VarietalUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class VarietalFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
