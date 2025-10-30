# app/support/subcategory/schemas.py

from typing import Optional

from pydantic import computed_field, ConfigDict, Field

from app.core.schemas.base import (CreateResponse, CreateSchemaSub, ReadApiSchema, ReadSchema, UpdateSchema)
from app.core.schemas.lang_schemas import (DetailViewEn, DetailViewFr, DetailViewRu,
                                           ListViewEn, ListViewFr, ListViewRu)
from app.support.category.schemas import CategoryCreateRelation, CategoryRead


class SubcategoryDetailViewEn(DetailViewEn):
    # category_id: Optional[int] = Field(exclude=True)
    category: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.category.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class SubcategoryDetailViewRu(DetailViewRu):
    category: ListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.category.display_name
        return f'{self.category.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class SubcategoryDetailViewFr(DetailViewFr):
    category: ListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.category.display_name
        return f'{self.category.display_name}. {self.name_fr or self.name or self.name_ru or ""}'

# --LIST VIEW-------------------------------


class SubcategoryListViewEn(ListViewEn):
    # category_id: Optional[int] = Field(exclude=True)
    category: ListViewEn = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        return (f'{self.category.display_name}.'
                f' {self.name or self.name_ru or self.name_fr or ""}')


class SubcategoryListViewRu(ListViewRu):
    category: ListViewRu = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.category.display_name
        return f'{self.category.display_name}. {self.name_ru or self.name or self.name_fr or ""}'


class SubcategoryListViewFr(ListViewFr):
    category: ListViewFr = Field(exclude=True)

    @computed_field(description='Name',  # Это будет подписью/лейблом (human readable)
                    title='Отображаемое имя'  # Это для swagger (machine readable)
                    )
    @property
    def display_name(self) -> str:
        """Возвращает первое непустое значение из name, name_ru, name_fr"""
        self.category.display_name
        return f'{self.category.display_name}. {self.name_fr or self.name or self.name_ru or ""}'


class CustomReadSchema:
    category: CategoryRead


class SubcategoryReadApiSchema(ReadApiSchema):
    category: ReadApiSchema = Field(exclude=True)

    def __get_lang__(self, lang: str = '_ru', ) -> str:
        schema, field_name = self.category, 'name'
        if schema:
            prefix = getattr(schema, f'{field_name}{lang}') or getattr(schema, f'{field_name}')
            return prefix
        return None

    @computed_field
    @property
    def category_ru(self) -> str:
        return self.__get_lang__('_ru')

    @computed_field
    @property
    def category_fr(self) -> str:
        return self.__get_lang__('_fr')

    @computed_field
    @property
    def category_en(self) -> str:
        return self.__get_lang__('')


class CustomCreateSchema:
    category_id: int


class CustomCreateRelation:
    category: CategoryCreateRelation


class CustomUpdSchema:
    category: Optional[CategoryCreateRelation]


class SubcategoryRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class SubcategoryCreateRelation(CreateSchemaSub, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryCreate(CreateSchemaSub, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class SubcategoryCreateResponseSchema(SubcategoryCreate, CreateResponse):
    pass
