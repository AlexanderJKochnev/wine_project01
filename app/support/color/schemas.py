# app/support/color/schemas.py


from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict


class CustomSchema:
    pass


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class ColorShort(ShortSchema):
    pass


class ColorRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class ColorCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class ColorUpdate(UpdateSchema, CustomUpdSchema):
    pass


class ColorFull(FullSchema, CustomSchema):
    pass
