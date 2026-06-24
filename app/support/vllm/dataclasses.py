# app.support.vllm.dataclasses.py
"""
дата классы для наборов данных
"""

from dataclasses import dataclass
from typing import Any, Dict, Tuple

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.core.config.project_config import settings
from app.core.utils.common_utils import jprint
from app.core.utils.pydantic_utils import inst_dict
from app.support import Category, Subcategory
from app.support.ollama.model import ISOLanguage, Prompt, Proption, WriterRule
from app.support.ollama.repository import PromptRepository, ProptionRepository, WriterRuleRepository


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
    subcategories: Tuple[Dict[Any, str]]

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
        subcategories = tuple(result.subcategory_ids)
        # получение субкатегорий
        model = Subcategory
        query = select(model).options(joinedload(model.category)).where(model.id.in_(subcategories))
        response = await session.scalars(query)
        subcat_dict = [inst_dict(instance) for instance in response.all()]
        jprint(subcat_dict)

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
        # получение описаний напитка на языке перевода (имена полей в subcat name name)
        # source_name: str = f'name{lang_dict.get(language_origin1)}'
        target_name: str = f'name{lang_dict.get(language_destination1)}'
        drink: str = subcat_dict.get(target_name, subcat_dict.get('name'))
        cat: dict = subcat_dict.get('category')
        category: str = cat.get(target_name, subcat_dict.get('name'))
        print(f'{drink=} {category=}')

        # 2. Возвращаем уже заполненный датакласс
        return cls(system_prompt=system_prompt,
                   user_prompt=user_prompt,
                   params=params,
                   language_origin=language_origin1,
                   language_destination=language_destination1,
                   chunk=chunk1,
                   source_field=source_field,
                   target_field=target_field,
                   subcategories=subcategories)
