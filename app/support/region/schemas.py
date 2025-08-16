# app/support/template/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.country.schemas import CountryShort
from pydantic import ConfigDict


class RegionCustom:
    # country_id: int
    pass


class RegionShort(ShortSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    country: CountryShort


class RegionRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    country: CountryShort


class RegionCreate(BaseSchema, RegionCustom):
    pass


class RegionUpdate(UpdateSchema, RegionCustom):
    pass


class RegionFull(FullSchema, RegionCustom):
    pass
