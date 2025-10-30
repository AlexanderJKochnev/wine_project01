# app/support/food/schemas.py

from typing import Optional

from pydantic import computed_field, ConfigDict, Field

from app.core.schemas.base import (CreateResponse, CreateSchema, ReadSchema, UpdateSchema)
from app.core.schemas.lang_schemas import (DetailViewEn, DetailViewFr, DetailViewRu, ListViewEn, ListViewFr, ListViewRu)
from app.support.superfood.schemas import SuperfoodCreateRelation, SuperfoodRead


# --- START DETAIL VIEW ---


class FoodDetailViewEn(DetailViewEn):
    # superfood_id: Optional[int] = Field(exclude=True)
    superfood: Optional[ListViewEn] = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.superfood.display_name if self.superfood else ""} '
                f' {self.name or self.name_ru or self.name_fr or ""}')


class FoodDetailViewRu(DetailViewRu):
    superfood: ListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.superfood.display_name
        return (f'{self.superfood.display_name if self.superfood else ""} '
                f'{self.name_ru or self.name or self.name_fr or ""}')


class FoodDetailViewFr(DetailViewFr):
    superfood: ListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.superfood.display_name
        return (f'{self.superfood.display_name if self.superfood else ""} '
                f'{self.name_fr or self.name or self.name_ru or ""}')

# --- END DETAIL VIEW -- START LIST VIEW -----


class FoodListViewEn(ListViewEn):
    # superfood_id: Optional[int] = Field(exclude=True)
    superfood: Optional[ListViewEn] = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.superfood.display_name if self.superfood else ""} '
                f' {self.name or self.name_ru or self.name_fr or ""}')


class FoodListViewRu(ListViewRu):
    superfood: ListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.superfood.display_name
        return (f'{self.superfood.display_name if self.superfood else ""} '
                f'{self.name_ru or self.name or self.name_fr or ""}')


class FoodListViewFr(ListViewFr):
    superfood: ListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.superfood.display_name
        return (f'{self.superfood.display_name if self.superfood else ""} '
                f'{self.name_fr or self.name or self.name_ru or ""}')

# --- END LIST VIEW ---


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
