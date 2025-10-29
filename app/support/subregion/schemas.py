# app/support/subregion/schemas.py

from typing import Optional

from pydantic import ConfigDict, Field, computed_field

from app.core.schemas.base import (CreateSchemaSub, FullSchema, ReadSchema, UpdateSchema, CreateResponse, ReadApiSchema)
from app.support.region.schemas import RegionCreateRelation, RegionRead, RegionReadApiSchema
from app.core.schemas.lang_schemas import (ListViewEn, ListViewFr, ListViewRu, ListView,
                                           DetailViewEn, DetailViewFr, DetailViewRu)


class SubregionListViewEn(ListView):
    region_id: Optional[int] = Field(exclude=True)
    region: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.region.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class SubregionListViewRu(ListViewRu):
    region: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.region.display_name
        return f'{self.region.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class SubregionListViewFr(ListViewFr):
    region: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.region.display_name
        return f'{self.region.display_name}. {self.name_fr or self.name or self.name_ru or ""}'


class SubregionReadApiSchema(ReadApiSchema):
    region: Optional[RegionReadApiSchema] = None


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


class SubregionCreate(CreateSchemaSub, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionCreateRelation(CreateSchemaSub, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubregionCreateResponseSchema(SubregionCreate, CreateResponse):
    pass
