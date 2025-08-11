# app/support/country/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from pydantic import ConfigDict



class CountryCustom:
    pass

class CountryShort(ShortSchema):
    pass


class CountryRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class CountryCreate(BaseSchema, CountryCustom):
    pass


class CountryUpdate(UpdateSchema, CountryCustom):
    pass


class CountryFull(FullSchema, CountryCustom):
    pass
