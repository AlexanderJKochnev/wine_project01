# app/support/sweetness/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class SweetnessShort(ShortSchema):
    pass


class SweetnessRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SweetnessCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SweetnessUpdate(UpdateSchema, CustomUpdSchema):
    pass


class SweetnessFull(FullSchema, CustomSchema):
    pass
