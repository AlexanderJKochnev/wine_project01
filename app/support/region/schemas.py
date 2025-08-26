# app/support/template/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema, PkSchema
from pydantic import ConfigDict, Field
from app.support.country.schemas import CountryShort, CountryPk
from typing import Optional


class CustomSchema:
    country: CountryShort


class CustomCreateSchema:
    country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionShort(ShortSchema):
    pass


class RegionRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
    country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")

class RegionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class RegionFull(FullSchema, CustomSchema):
    pass
