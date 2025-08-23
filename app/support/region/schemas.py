# app/support/template/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict
from app.support.country.schemas import CountryShort
from typing import Optional

class CustomSchema:
    country: CountryShort


class CustomCreateSchema:
    country_id: int


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionShort(ShortSchema):
    pass


class RegionRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class RegionFull(FullSchema, CustomSchema):
    pass
