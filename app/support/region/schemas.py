# app/support/region/schemas.py

from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import (CreateSchema, FullSchema, ReadSchema, CreateResponse, UpdateSchema)
from app.support.country.schemas import CountryCreateRelation, CountryRead


class CustomCreateRelation:
    country: CountryCreateRelation


class CustomReadSchema:
    country: CountryRead


class CustomCreateSchema:
    country_id: int


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreateResponseSchema(RegionCreate, CreateResponse):
    pass
