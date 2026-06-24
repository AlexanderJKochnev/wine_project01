# app.support.vllm.dataclasses.py
"""
дата классы для наборов данных
"""

from dataclasses import dataclass
from typing import List

from sqlalchemy import select

from app.core.config.project_config import settings
from app.core.utils.pydantic_utils import inst_dict
from app.support.ollama.model import ISOLanguage, Prompt, Proption, WriterRule
from app.support.ollama.repository import ISOLanguageRepository, PromptRepository, ProptionRepository, \
    WriterRuleRepository


@dataclass(slots=True)  # без __dict__ +скорость/меньше память
class DrinkTranslateData:
    system_prompt: tuple  # result.id, result.system_prompt, result.role
    user_prompt: tuple    # result.id, result.prompt, result.name
    language_origin: str  # English
    language_destination: str  # English
    params: dict
    chunk: int
    source_field: str   # destination_ru
    target_field: str   # destination_ru

    @classmethod
    async def load_from_db(cls,
                           system: str,
                           user: str,
                           proption: str,
                           language_origin1: str,
                           language_destination1: str,
                           chunk1: int,
                           field: str,
                           session):
        """Асинхронный фабричный метод для создания объекта."""
        result: Prompt = await PromptRepository.get_by_field_v2({'role': system}, Prompt, session)
        system_prompt = result.id, result.system_prompt, result.role
        result: WriterRule = await WriterRuleRepository.get_by_field_v2({'name': user}, WriterRule, session)
        user_prompt = result.id, result.prompt, result.name
        result: Proption = await ProptionRepository.get_by_field_v2({'preset': proption}, Proption, session)
        params = inst_dict(result)
        # получение двух суффиксов языков сразу
        model = ISOLanguage
        query = (select(model.name_en, model.iso_639_1)
                 .where(ISOLanguage.name_en.in_((language_origin1, language_destination1))))
        result = await session.execute(query)
        def_lang: str = settings.DEFAULT_LANG
        lang_dict = {name: '' if lang == def_lang else f'_{lang}' for name, lang in result}
        source_field: str = f'{field}{lang_dict.get(language_origin1)}'
        target_field: str = f'{field}{lang_dict.get(language_destination1)}'

        # 2. Возвращаем уже заполненный датакласс
        return cls(system_prompt=system_prompt,
                   user_prompt=user_prompt,
                   params=params,
                   language_origin=language_origin1,
                   language_destination=language_destination1,
                   chunk=chunk1,
                   source_field=source_field,
                   target_field=target_field)