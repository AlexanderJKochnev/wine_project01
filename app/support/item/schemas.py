# app/support/item/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class ItemShort(ShortSchema):
    pass


class ItemRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemUpdate(UpdateSchema, CustomUpdSchema):
    pass


class ItemFull(FullSchema, CustomSchema):
    pass
