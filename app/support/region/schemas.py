# app/support/region/schemas.py

from typing import Optional

from pydantic import ConfigDict, Field

from app.core.schemas.base import (CreateSchema, DateSchema, PkSchema, ReadSchemaWithRealtionships, ShortSchema,
                                   UpdateSchema)
from app.support.country.schemas import CountryShort


class CustomSchema:
    country: Optional[CountryShort] = None


class CustomCreateSchema:
    country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionShort(ShortSchema, CustomSchema):
    pass


class RegionRead(ReadSchemaWithRealtionships):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # protected_namespaces=('_',),
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    country: Optional[str] = None


class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
    # country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class RegionCreateResponseSchema(RegionCreate, PkSchema, DateSchema):
    pass
