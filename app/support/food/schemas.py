# app/support/food/schemas.py

from pydantic import ConfigDict, Field, computed_field
from typing import Optional
from app.core.schemas.base import (CreateSchema, ReadSchema, UpdateSchema, CreateResponse)
from app.support.superfood.schemas import SuperfoodRead, SuperfoodCreateRelation
from app.core.schemas.lang_schemas import (ListViewEn, ListViewFr, ListViewRu, ListView,
                                           DetailViewEn, DetailViewFr, DetailViewRu)


class FoodListViewEn(ListView):
    superfood_id: Optional[int] = Field(exclude=True)
    superfood: Optional[ListViewEn] = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.superfood.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class FoodListViewRu(ListViewRu):
    superfood: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.superfood.display_name
        return f'{self.superfood.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class FoodListViewFr(ListViewFr):
    superfood: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.superfood.display_name
        return f'{self.superfood.display_name}. {self.name_fr or self.name or self.name_ru or ""}'


class CustomReadSchema:
    superfood: Optional[SuperfoodRead] = None


class CustomCreateSchema:
    superfood_id: int


class CustomCreateRelation:
    superfood: SuperfoodCreateRelation


class CustomUpdSchema:
    superfood: Optional[SuperfoodCreateRelation] = None


class FoodRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class FoodCreateResponseSchema(FoodCreate, CreateResponse):
    pass
