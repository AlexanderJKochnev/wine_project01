# app/support/subcategory/schemas.py

from typing import Optional

from pydantic import computed_field, ConfigDict, Field

from app.core.schemas.base import (CreateResponse, CreateSchemaSub, ReadApiSchema, ReadSchema, UpdateSchema)
from app.support.category.schemas import CategoryCreateRelation, CategoryRead


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
