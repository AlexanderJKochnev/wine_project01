# app/support/subregion/schemas.py

from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import (CreateSchema, FullSchema, ReadSchema, UpdateSchema)
from app.support.region.schemas import RegionCreateRelation, RegionRead


class CustomCreateRelation:
    region: RegionCreateRelation


class CustomReadSchema:
    region: Optional[RegionRead] = None


class CustomCreateSchema:
    region_id: int


class CustomUpdSchema:
    region_id: Optional[int] = None


class SubregionRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
