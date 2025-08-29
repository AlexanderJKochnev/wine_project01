# app/support/region/schemas.py

from typing import Optional

from pydantic import ConfigDict, Field

from app.core.schemas.base import (CreateSchema, PkSchema, ReadSchema,
                                   ShortSchema, UpdateSchema, DateSchema)
from app.support.country.schemas import CountryShort


class CustomSchema:
    country: CountryShort


class CustomCreateSchema:
    country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class CustomUpdSchema:
    country_id: Optional[int] = None


class RegionShort(ShortSchema, CustomSchema):
    pass


class RegionRead(ReadSchema, CustomSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # populate_by_name=True,
                              )  # , exclude_none=True)


"""    def dict(self, **kwargs):
        # Переопределяем dict() чтобы получить плоскую структуру
        result = super().dict(**kwargs)
        for key, val in result.items():
            if not isinstance(val, dict):
                continue
            val = 'тест'
"""


class RegionCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
    # country_id: int = Field(..., description="ID страны (Country.id) для связи Many-to-One")


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class RegionCreateResponseSchema(RegionCreate, PkSchema, DateSchema):
    pass
