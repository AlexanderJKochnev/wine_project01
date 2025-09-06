# app/support/color/schemas.py


from app.core.schemas.base import CreateSchema, ReadSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomReadSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class ColorRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
