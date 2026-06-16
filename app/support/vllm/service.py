# app.support.vllm.service.py
from typing import Any, List

from fastapi import BackgroundTasks
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.core.repositories.sqlalchemy_repository import Repository
from app.core.services.service import Service
from app.core.services.translate_service import TranslationService
from app.core.types import ModelType
from app.support import Drink, DrinkService
from app.support.drink.repository import DrinkRepository
# from app.core.utils.common_utils import jprint
from app.support.ollama.model import ISOLanguage, Prompt, Proption, WriterRule
from app.support.ollama.repository import ISOLanguageRepository, PromptRepository, ProptionRepository, \
    WriterRuleRepository


class VLLMService:
    """
    1. получение даннных
    2. загрузка: prompt, preset, langs, proption
    3. подготовка запроса
    """

    def __init__(self):
        # vLLM по умолчанию работает на http://localhost:8000/v1
        self.client = AsyncOpenAI(
            base_url='http://vllm-node:8000/v1/',
            api_key="token-not-needed"
        )
        self.model_name = "/model"  # "Qwen/Qwen2.5-7B-Instruct-GPTQ"

    async def get_translate2(self, phrase: str, prompt: str, proption: str, writer: str, lang: str,
                             drink,
                             session: AsyncSession, translation_service: TranslationService,
                             **kwargs):
        # получаем phrase, prompt, preset, writer, lang, session
        # собираем payload
        dataset = {'prompt': (Prompt, PromptRepository, 'role', 'system_prompt', prompt),
                   'writer': (WriterRule, WriterRuleRepository, 'name', 'prompt', writer),
                   'proption': (Proption, ProptionRepository, 'preset', None, proption),
                   # 'lang': (ISOLanguage, ISOLanguageRepository, 'iso_639_1', 'name_en', lang)
                   }
        payload: dict = {}
        payload["lang"] = lang
        for key, val in dataset.items():
            model, repo, field_name, field_out, search = val
            tmp: ModelType = await repo.get_by_field(field_name, search, model, session)
            if field_out:
                payload[key] = getattr(tmp, field_out)
            else:
                # payload['params'] = tmp.to_dict()
                payload.update(tmp.to_dict())
        payload.pop('category_id')
        result = await translation_service.translate(phrase, payload.pop('prompt'),
                                                     payload.pop('writer'), payload.pop('lang'),
                                                     drink,
                                                     **payload)
        return result

    async def bulk_test(self, background_tasks: BackgroundTasks,
                        session: AsyncSession, translation_service: TranslationService,
                        subcat: str, chunk: int, lang: str):
        """
            это тестирование качества перевода
            по катерогриям/субкатегориям напитков
            по результатам тестирования будут выбраны лучшие авторы для каждой субкатегории напитков
            поэтому сейчас их привязка к категориям не учитывается
        """
        (ISOLanguage, ISOLanguageRepository, 'iso_639_1', 'name_en', lang)
        data = await self.get_data(background_tasks, session, subcat, chunk)
        return data

    @staticmethod
    async def get_source(model: ModelType, repo: Repository,
                         session: AsyncSession, id_field: str = None, out_field: str = None,
                         value: Any = None):
        """ получение данных из базы данных:
            if all args are not null: return Tuple[id: out_filed.value]
            if value is null: return List[Tuple[id, out_filed.value]]
            if all args are null: return Tuple
            если все данные is null - return list of dict
        """
        if value:
            filter = {id_field: value}
            tmp: ModelType = await repo.get_by_field_v2(filter=filter, model=model, session=session)

    async def get_data(self, background_tasks: BackgroundTasks, session: AsyncSession, subcat: str,
                       chunk: int  # размер тестовой выборки
                       ) -> dict:
        service = DrinkService
        if subcat.isnumeric():
            filters = {'id': int(subcat)}
        else:
            filters = {'name': subcat}
        root_filter = {'description_ru': None}
        repository = DrinkRepository
        related_model_name = 'Subcategory'
        model = Drink
        result = await service.get_with_filter_complex(background_tasks, session, model,
                                                       related_model_name, repository,
                                                       filters, root_filter, 1, 20, 0)
        items = result.get('items')
        if not items:
            return None
        source: dict = {key.get('id'): key.get('description') for key in items}
        # {id: description, ...}
        return source


class TranslateRawDataService(Service):
    default = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']
