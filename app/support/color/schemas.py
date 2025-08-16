# app/support/color/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema


class ColorCustom:
    category_id: int


class ColorShort(ShortSchema):
    pass


class ColorRead(BaseSchema):
    pass


class ColorCreate(BaseSchema, ColorCustom):
    pass


class ColorUpdate(UpdateSchema, ColorCustom):
    pass


class ColorFull(FullSchema, ColorCustom):
    pass
