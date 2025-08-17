# app/support/color/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema


class ColorCustom:
    pass


class ColorShort(ShortSchema):
    pass


class ColorRead(BaseSchema, ColorCustom):
    pass


class ColorCreate(BaseSchema, ColorCustom):
    pass


class ColorUpdate(UpdateSchema, ColorCustom):
    pass


class ColorFull(FullSchema, ColorCustom):
    pass
