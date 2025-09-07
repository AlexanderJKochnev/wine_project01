# app/support/region/schemas.py

from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import (CreateSchema, ReadSchema, ReadSchemaWithRealtionships,
                                   UpdateSchema, FullSchema)
from app.support.country.schemas import CountryRead


class CustomReadSchema:
    country: Optional[CountryRead] = None


class CustomCreateSchema:
    country_id: int


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionRead1(ReadSchemaWithRealtionships):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # protected_namespaces=('_',),
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    country: Optional[str] = None
