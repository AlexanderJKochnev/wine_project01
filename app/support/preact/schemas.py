# app/support/preact/schemas.py
"""
    lang:
        handbooks (read only):
            subcategory -> category
            subregion -> region -> country
            subcategory -> category
            varietals
            pairing
        create with hierarchy (hanbooks lang)
            image add
        read
    path
        image delete
        image add
    delete
"""
from pydantic import Field, BaseModel, computed_field
from app.core.schemas.base import NameSchema, PyModel, NameExcludeSchema


def get_lang(schema: PyModel, lang: str = '', field_name: str = 'name') -> str:
    """
    получение значения на языке lang
    :param self:
    :type self:
    :param lang:
    :type lang:
    :return:
    :rtype:
    """
    value = getattr(schema, f'{field_name}{lang}') or getattr(schema, f'{field_name}')
    return value


class CategoryHandBook(NameSchema):
    pass


class SubCategoryHB(NameExcludeSchema):
    category: CategoryHandBook = Field(exclude=True)
    id: int = Field(exclude=True)

    @computed_field
    @property
    def iname(self) -> str:
        field_name = 'name'
        lang = '_ru'
        name = getattr(self, f'{field_name}{lang}') or getattr(self, f'{field_name}')
        parent = get_lang(self.category)
        return f'{parent}. {name}'


class SubCategoryHB_Ru(BaseModel):
    category: NameSchema = Field(exclude=True)
    id: int = Field(exclude=True)

    @computed_field
    @property
    def name(self) -> str:
        return get_lang(self.category, lang='_ru')


class SubCategoryHB_Fr(BaseModel):
    category: NameSchema = Field(exclude=True)
    id: int = Field(exclude=True)

    @computed_field
    @property
    def name(self) -> str:
        return get_lang(self.category, lang='_fr')


class CountryHandBook(NameSchema):
    pass


class RegionHandBook(NameSchema):
    country: CountryHandBook = Field(exclude=True)