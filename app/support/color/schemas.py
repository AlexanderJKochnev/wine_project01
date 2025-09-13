# app/support/color/schemas.py

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


class ColorRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ColorCreateResponseSchema(ColorCreate, CreateResponse):
    pass
