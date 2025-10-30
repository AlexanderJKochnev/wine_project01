# app/support/region/schemas.py

from typing import Optional

from pydantic import computed_field, ConfigDict, Field

from app.core.schemas.base import (CreateResponse, CreateSchemaSub, ReadApiSchema, ReadSchema, UpdateSchema)
from app.core.schemas.lang_schemas import (DetailViewEn, DetailViewFr, DetailViewRu, ListViewEn, ListViewFr, ListViewRu)
from app.support.country.schemas import CountryCreateRelation, CountryRead


# -----------------DETAIL VIEW START

class RegionDetailViewEn(DetailViewEn):
    # country_id: Optional[int] = Field(exclude=True)
    country: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.country.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class RegionDetailViewRu(DetailViewRu):
    country: ListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.country.display_name
        return f'{self.country.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class RegionDetailViewFr(DetailViewFr):
    country: ListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.country.display_name
        return f'{self.country.display_name}. {self.name_fr or self.name or self.name_ru or ""}'

# -------DETAIL VIEW END----------LIST VIEW START--------


class RegionListViewEn(ListViewEn):
    # country_id: Optional[int] = Field(exclude=True)
    country: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.country.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class RegionListViewRu(ListViewRu):
    country: ListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.country.display_name
        return f'{self.country.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class RegionListViewFr(ListViewFr):
    country: ListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.country.display_name
        return f'{self.country.display_name}. {self.name_fr or self.name or self.name_ru or ""}'

# -------LIST VIEW END-----------


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


class RegionCreate(CreateSchemaSub, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreateRelation(CreateSchemaSub, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class RegionCreateResponseSchema(RegionCreate, CreateResponse):
    pass
