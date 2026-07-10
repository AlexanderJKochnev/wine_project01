# app.support.vllm.dataclasses.py
"""
дата классы для наборов данных
"""

from dataclasses import dataclass
from typing import Dict, Optional

import ahocorasick
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.core.config.project_config import settings
from app.core.enum import HANDBOOKS
from app.core.utils.ahocorasick import get_extractor
from app.core.utils.common_utils import distinct_glue, jprint
from app.core.utils.pydantic_utils import inst_dict
from app.support import Subcategory
from app.support.ollama.model import ISOLanguage, Prompt, Proption, WriterRule
from app.support.ollama.repository import ProptionRepository


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
    subcategories: Dict  # Tuple[Dict[Any, str]] описание: словарь subcategory_id: описание
    score_threshold: int  # приемлемая оценка
    lang_origin: str  # 2х значный код
    lang_destin: str  # 2х значный код
    subcategory_ids: tuple  # ids
    expert_system_prompt: tuple
    expert_user_prompt: tuple
    cleaner_auto: Optional[ahocorasick.Automaton] = None
    translator_auto: Optional[ahocorasick.Automaton] = None
    descr: Optional[str] = None  # описание - совместимость с Handbook

    @classmethod
    async def load_from_db(cls,
                           system: str,
                           user: str,
                           proption: str,
                           language_origin1: str,
                           language_destination1: str,
                           chunk1: int,
                           field: str,
                           score: int,
                           expert_system: str,
                           expert_user: str,
                           session: AsyncSession):
        """Асинхронный фабричный метод для создания объекта."""
        # result: Prompt = await PromptRepository.get_by_field_v2({'role': system}, Prompt, session)
        # system_prompt = result.id, result.system_prompt, result.role
        query = (select(Prompt.id, Prompt.system_prompt, Prompt.role).where(Prompt.role.in_((system, expert_system))))
        resp = await session.execute(query)
        prompts = {row.role: (row.id, row.system_prompt, row.role) for row in resp.all()}
        system_prompt = prompts.get(system)
        expert_system_prompt = prompts.get(expert_system)
        # user prompts
        query = (select(WriterRule.id, WriterRule.prompt, WriterRule.name,
                 WriterRule.subcategory_ids).where(WriterRule.name.in_((user, expert_user))))
        resp = await session.execute(query)
        prompts = {row.name: (row.id, row.prompt, row.name, row.subcategory_ids) for row in resp.all()}
        *user_prompt, subcategory_ids = prompts.get(user)
        *expert_user_prompt, _ = prompts.get(expert_user)
        # result: WriterRule = await WriterRuleRepository.get_by_field_v2({'name': user}, WriterRule, session)
        # user_prompt = result.id, result.prompt, result.name

        # получение субкатегорий
        model = Subcategory
        query = select(model).options(joinedload(model.category)).where(model.id.in_(subcategory_ids))
        response = await session.scalars(query)
        subcat_dict = [inst_dict(instance) for instance in response.all()]
        result: Proption = await ProptionRepository.get_by_field_v2({'preset': proption}, Proption, session)
        params = inst_dict(result)
        # получение двух суффиксов языков сразу
        model = ISOLanguage
        query = (select(model.name_en, model.iso_639_1)
                 .where(ISOLanguage.name_en.in_((language_origin1, language_destination1))))
        resp = await session.execute(query)
        result: dict = dict(resp.all())
        def_lang: str = settings.DEFAULT_LANG
        lang_dict = {name: '' if lang == def_lang else f'_{lang}' for name, lang in result.items()}
        source_field: str = f'{field}{lang_dict.get(language_origin1)}'
        target_field: str = f'{field}{lang_dict.get(language_destination1)}'
        # получение описаний напитка на языке перевода (имена полей в subcat name name)
        # source_name: str = f'name{lang_dict.get(language_origin1)}'
        target_name: str = f'name{lang_dict.get(language_destination1)}'
        lang_origin = result.get(language_origin1)
        lang_destin = result.get(language_destination1)
        # загрузка боров
        cleaner_auto: ahocorasick.Automaton = await get_extractor('cleaner', session, {'shit': True})
        task_type: str = f'translator_{lang_origin}_{lang_destin}'
        db_filter: dict = {'shit': False, 'origin': lang_origin, 'destin': lang_destin}
        translator_auto: ahocorasick.Automaton = await get_extractor(task_type, session, db_filter)
        # описание: словарь subcategory_id: описание
        drink: dict = {item.get('id'): (distinct_glue(item.get(target_name, item.get('name')),
                                        item['category'].get(target_name,
                                                             item['category'].get('name')),
            blacklist=('other', 'brandy', 'прочее', 'бренди')
        )) for item in subcat_dict}
        jprint(drink)

        # 2. Возвращаем уже заполненный датакласс
        return cls(system_prompt=system_prompt,
                   user_prompt=user_prompt,
                   params=params,
                   language_origin=language_origin1,
                   language_destination=language_destination1,
                   chunk=chunk1,
                   source_field=source_field,
                   target_field=target_field,
                   subcategories=drink,
                   score_threshold=score,
                   lang_destin=lang_destin,
                   lang_origin=lang_origin,
                   translator_auto=translator_auto,
                   cleaner_auto=cleaner_auto,
                   subcategory_ids=subcategory_ids,
                   expert_system_prompt=expert_system_prompt,
                   expert_user_prompt=expert_user_prompt)


@dataclass(slots=True)
class HandbookTranslateData:
    """
    отличается от DrinkTranslateData полями handbook и subcategoty_id соотвественно
    """
    system_prompt: tuple  # result.id, result.system_prompt, result.role
    user_prompt: tuple    # result.id, result.prompt, result.name
    language_origin: str  # English
    language_destination: str  # Russian
    params: dict
    chunk: int
    source_field: str   # destination_ru
    target_field: str   # destination_ru
    handbook: str  # handbook table
    descr: str  # описание (drink)
    score_threshold: int
    lang_origin: str  # 2х значный код
    lang_destin: str  # 2х значный код
    expert_system_prompt: tuple
    expert_user_prompt: tuple
    cleaner_auto: Optional[ahocorasick.Automaton] = None
    translator_auto: Optional[ahocorasick.Automaton] = None

    @classmethod
    async def load_from_db(cls,
                           system: str,
                           user: str,
                           proption: str,
                           language_origin1: str,
                           language_destination1: str,
                           chunk1: int,
                           field: str,
                           handbook1: str,  #
                           score: int,
                           expert_system: str,
                           expert_user: str,
                           session: AsyncSession):
        """Асинхронный фабричный метод для создания объекта."""
        query = (select(Prompt.id, Prompt.system_prompt, Prompt.role).where(Prompt.role.in_((system, expert_system))))
        resp = await session.execute(query)
        prompts = {row.role: (row.id, row.system_prompt, row.role) for row in resp.all()}
        system_prompt = prompts.get(system)
        expert_system_prompt = prompts.get(expert_system)
        # user prompts
        query = (select(WriterRule.id, WriterRule.prompt, WriterRule.name)
                 .where(WriterRule.name.in_((user, expert_user))))
        resp = await session.execute(query)
        prompts = {row.name: (row.id, row.prompt, row.name) for row in resp.all()}
        user_prompt = prompts.get(user)
        expert_user_prompt = prompts.get(expert_user)

        descr = HANDBOOKS.get(handbook1)
        # получение params
        result: Proption = await ProptionRepository.get_by_field_v2({'preset': proption}, Proption, session)
        params = inst_dict(result)
        # получение двух суффиксов языков сразу
        model = ISOLanguage
        query = (select(model.name_en, model.iso_639_1)
                 .where(ISOLanguage.name_en.in_((language_origin1, language_destination1))))
        resp = await session.execute(query)
        result: dict = dict(resp.all())
        def_lang: str = settings.DEFAULT_LANG
        lang_dict = {name: '' if lang == def_lang else f'_{lang}' for name, lang in result.items()}
        source_field: str = f'{field}{lang_dict.get(language_origin1)}'
        target_field: str = f'{field}{lang_dict.get(language_destination1)}'
        lang_origin = result.get(language_origin1)
        lang_destin = result.get(language_destination1)
        # загрузка боров
        cleaner_auto: ahocorasick.Automaton = await get_extractor('cleaner', session, {'shit': True})
        task_type: str = f'translator_{lang_origin}_{lang_destin}'
        db_filter: dict = {'shit': False, 'origin': lang_origin, 'destin': lang_destin}
        translator_auto: ahocorasick.Automaton = await get_extractor(task_type, session, db_filter)

        # 2. Возвращаем уже заполненный датакласс
        return cls(system_prompt=system_prompt,
                   user_prompt=user_prompt,
                   params=params,
                   language_origin=language_origin1,
                   language_destination=language_destination1,
                   chunk=chunk1,
                   source_field=source_field,
                   target_field=target_field,
                   handbook=handbook1,
                   descr=descr,
                   score_threshold=score,
                   lang_destin=lang_destin,
                   lang_origin=lang_origin,
                   translator_auto=translator_auto,
                   cleaner_auto=cleaner_auto,
                   expert_system_prompt=expert_system_prompt,
                   expert_user_prompt=expert_user_prompt
                   )


@dataclass(slots=True)
class LastComposite:
    last_id: Optional[int] = None
    last_subcategory: Optional[int] = None


@dataclass(slots=True)
class TranslateHelpData:
    word: str
    language_origin: str  # English
    language_destination: str  # Russian
    origin: str  # ru, ''
    destin: str  # ru, ''
    approved: bool

    @classmethod
    async def load_from_db(cls, word1: str,
                           language_origin1: str,
                           language_destination1: str,
                           approved1: bool,
                           session: AsyncSession):
        model = ISOLanguage
        query = (select(model.name_en, model.iso_639_1).where(
            ISOLanguage.name_en.in_((language_origin1, language_destination1))
        ))
        resp = await session.execute(query)
        result: dict = dict(resp.all())
        def_lang: str = settings.DEFAULT_LANG
        lang_dict = {name: '' if lang == def_lang else f'_{lang}' for name, lang in result.items()}
        origin: str = f'{lang_dict.get(language_origin1)}'
        destin: str = f'{lang_dict.get(language_destination1)}'
        # source_field: str = f'{field}{lang_dict.get(language_origin1)}'
        # target_field: str = f'{field}{lang_dict.get(language_destination1)}
        return cls(word=word1,
                   language_destination=language_destination1,
                   language_origin=language_origin1,
                   origin=origin,
                   destin=destin,
                   approved=approved1)
