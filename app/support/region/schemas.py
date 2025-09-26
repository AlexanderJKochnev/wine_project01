# app/support/region/schemas.py

from typing import Optional

from pydantic import ConfigDict, Field, computed_field

from app.core.schemas.base import (CreateSchema, FullSchema, ReadSchema, CreateResponse, UpdateSchema, ReadApiSchema)
from app.support.country.schemas import CountryCreateRelation, CountryRead


class RegionReadApiSchema(ReadApiSchema):
    country: ReadApiSchema = Field(exclude=True)
    
    def __get_lang__(self, lang: str = '_ru', ) -> str:
        schema, field_name = self.country, 'name'
        if schema:
            prefix = getattr(schema, f'{field_name}{lang}') or getattr(schema, f'{field_name}')
            return prefix
        return None
    
    @computed_field
    @property
    def country_ru(self) -> str:
        return self.__get_lang__('_ru')
    
    @computed_field
    @property
    def country_fr(self) -> str:
        return self.__get_lang__('_fr')
    
    @computed_field
    @property
    def country_en(self) -> str:
        return self.__get_lang__('')


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
