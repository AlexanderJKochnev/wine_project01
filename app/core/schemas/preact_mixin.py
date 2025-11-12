# app/core/schemas/preact_mixin.py
from pydantic import computed_field
from app.core.schemas.base import NameExcludeSchema


class PreactLangMixin(NameExcludeSchema):
    """
        языковая схема - возвращает поле <name> на заданном языке или англ
    """

    def __get_lang__(self, schema, lang: str = '', field_name: str = 'name') -> str:
        return getattr(schema, f'{field_name}{lang}') or getattr(schema, f'{field_name}')

    @computed_field
    @property
    def iname(self) -> str:
        return self.__get_lang__('_ru')
