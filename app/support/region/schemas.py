# app/support/region/schemas.py

from typing import Optional

from pydantic import computed_field, Field

from app.core.schemas.base import (CreateResponse, CreateSchemaSub, ReadApiSchema, ReadSchema, UpdateSchema,
                                   DetailView, ListView)
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
    pass


class RegionReadRelation(RegionRead):
    pass


class RegionCreate(CreateSchemaSub, CustomCreateSchema):
    pass


class RegionCreateRelation(CreateSchemaSub, CustomCreateRelation):
    pass


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class RegionCreateResponseSchema(RegionCreate, CreateResponse):
    pass


class RegionDetailView(DetailView):
    country: Optional[ListView] = None