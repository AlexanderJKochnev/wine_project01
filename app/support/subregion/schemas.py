# app/support/subregion/schemas.py

from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import (CreateSchema, ReadSchema, ReadSchemaWithRealtionships,
                                   UpdateSchema, FullSchema)


class CustomReadSchema:
    country: Optional[str] = None


class CustomCreateSchema:
    country_id: int


class CustomUpdSchema:
    country_id: Optional[int] = None


class SubregionRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionRead1(ReadSchemaWithRealtionships):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # protected_namespaces=('_',),
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    country: Optional[str] = None
