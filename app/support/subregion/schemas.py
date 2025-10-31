# app/support/subregion/schemas.py

from typing import Optional

from pydantic import computed_field, Field

from app.core.schemas.base import (CreateResponse, CreateSchemaSub, FullSchema, ReadApiSchema, ReadSchema, UpdateSchema)
from app.core.schemas.lang_schemas import (DetailViewEn, DetailViewFr, DetailViewRu, ListViewEn, ListViewFr, ListViewRu)
from app.support.region.schemas import RegionCreateRelation, RegionListViewEn, RegionListViewFr, RegionListViewRu, \
    RegionRead, RegionReadApiSchema


# -----------DETAIL VIEW START ------------


class SubregionDetailViewEn(DetailViewEn):
    # region_id: Optional[int] = Field(exclude=True)
    region: RegionListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.region.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class SubregionDetailViewRu(DetailViewRu):
    region: RegionListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.region.display_name
        return f'{self.region.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class SubregionDetailViewFr(DetailViewFr):
    region: RegionListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.region.display_name
        return f'{self.region.display_name}. {self.name_fr or self.name or self.name_ru or ""}'

# -----------END DETAIL ---- START LIST-----


class SubregionListViewEn(ListViewEn):
    #  region_id: Optional[int] = Field(exclude=True)
    region: RegionListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.region.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class SubregionListViewRu(ListViewRu):
    region: RegionListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.region.display_name
        return f'{self.region.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class SubregionListViewFr(ListViewFr):
    region: RegionListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.region.display_name
        return f'{self.region.display_name}. {self.name_fr or self.name or self.name_ru or ""}'

# -------- END LIST VIEW --------------


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
    pass


class SubregionReadRelation(SubregionRead):
    pass


class SubregionCreate(CreateSchemaSub, CustomCreateSchema):
    pass


class SubregionCreateRelation(CreateSchemaSub, CustomCreateRelation):
    pass


class SubregionUpdate(UpdateSchema, CustomUpdSchema):
    pass


class SubregionFull(FullSchema, CustomReadSchema):
    pass


class SubregionCreateResponseSchema(SubregionCreate, CreateResponse):
    pass
