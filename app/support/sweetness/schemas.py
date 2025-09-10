# app/support/sweetness/schemas.py

from pydantic import ConfigDict

from app.core.schemas.base import CreateSchema, FullSchema, ReadSchema, UpdateSchema


class CustomCreateRelation:
    pass


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class SweetnessRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SweetnessCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SweetnessCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SweetnessUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SweetnessFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
