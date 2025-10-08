# app/core/schemas/api_mixin.py
from pydantic import computed_field

from app.core.schemas.base import BaseModel


class LangMixin(BaseModel):
    """ языковая схема - добавлять 'name_<lang>' """

    def __get_schmema__(self):
        schema = None
        field_name = None
        return schema, field_name

    def __get_lang__(self, lang: str = '_ru', ) -> str:
        schema, field_name = self.__get_schmema__()
        if schema:
            prefix = getattr(schema, f'{field_name}{lang}') or getattr(schema, f'{field_name}')
            return prefix
        return None

    @computed_field
    @property
    def name_ru(self) -> str:
        return self.__get_lang__('_ru')

    @computed_field
    @property
    def name_fr(self) -> str:
        return self.__get_lang__('_fr')

    @computed_field
    @property
    def name(self) -> str:
        return self.__get_lang__('')
