# app.support.vllm.service.py
from typing import List, Tuple
from app.core.utils.common_utils import jprint
from fastapi import BackgroundTasks
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
from app.core.services.translate_service import TranslationService
from app.core.types import ModelType
from app.core.utils.pydantic_utils import inst_dict, list_dict
from app.support import Drink, DrinkService, Subcategory, TranslateRawData
from app.support.drink.repository import DrinkRepository
# from app.core.utils.common_utils import jprint
from app.support.ollama.model import Prompt, Proption, WriterRule
from app.support.ollama.repository import PromptRepository, ProptionRepository, WriterRuleRepository
from app.support.subcategory.repository import SubcategoryRepository
from app.support.vllm.repository import TranslateRawDataRepository


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
        # список данных для перевода
        def get_subcat_filter(subcat: str):
            if subcat.isnumeric():
                filters = {'id': int(subcat)}
            else:
                filters = {'name': subcat}
            return filters

        subcat_dict = get_subcat_filter(subcat)
        language: str = lang
        logger.critical(f'{language}')
        return {'result': language}
        drink: str = await self.get_subcategiory(subcat_dict, session)
        system_prompts: List[Tuple] = await self.get_system_prompts(session)
        user_prompts: List[Tuple] = await self.get_user_prompt(session)
        proption: List[dict] = await self.get_proption(session)
        payload = {'system_prompts': system_prompts,
                   'user_prompts': user_prompts,
                   'lang': language,
                   'drink': drink,
                   'params': proption}
        data: List = await self.get_data(background_tasks, session, subcat_dict, chunk, payload, translation_service)
        return data

    @staticmethod
    async def get_system_prompts(session: AsyncSession):
        """
            получение списка промптов
        """
        model, repo = Prompt, PromptRepository
        filter = {'active': True}
        response: List[Prompt] = await repo.get_list_by_field_v2(filter=filter, model=model, session=session)
        if response:
            return [(inst.id, inst.system_prompt) for inst in response]

    @staticmethod
    async def get_user_prompt(session: AsyncSession) -> List[Tuple]:
        """
            получение списка промптов
        """
        model, repo = WriterRule, WriterRuleRepository
        filter = {'active': True}
        response: List[WriterRule] = await repo.get_list_by_field_v2(filter=filter, model=model, session=session)
        if response:
            return [(inst.id, inst.prompt) for inst in response]

    @staticmethod
    async def get_proption(session: AsyncSession) -> List[dict]:
        """
            получение списка настроек
        """
        model, repo = Proption, ProptionRepository
        filter = {'active': True}
        response: List[WriterRule] = await repo.get_list_by_field_v2(filter=filter, model=model, session=session)
        if response:
            return list_dict(response)

    @staticmethod
    async def get_subcategiory(filters: dict, session: AsyncSession) -> str:
        """
        получение субкатегории на языке перевода
        """
        # 1 суффикс языка - берем русский
        model, repo = Subcategory, SubcategoryRepository
        response: Subcategory = await repo.get_by_field_v2(filters, model, session)
        # jprint(inst_dict(response))
        cat = response.category.name_ru or response.category.name or response.category.name_fr or ""
        subc = response.name_ru or response.name or response.name_fr or ""
        # subcat is empty:
        if subc == "":
            result = cat.strip().lower()
        elif cat.lower().strip() in subc.lower():
            result = subc.strip().lower()
        else:
            exclude_list = ('brandy', 'other')
            if response.category.name.lower().strip() in exclude_list:
                result = subc.strip().lower()
            else:
                result = f'{subc} {cat}'.strip().lower()
        # logger.critical(f'{result=}')
        return result

    async def get_data(self,
                       background_tasks: BackgroundTasks,
                       session: AsyncSession,
                       subcat: dict,
                       chunk: int,  # размер тестовой выборки
                       payload: dict,
                       translation_service: TranslationService
                       ) -> List[Tuple]:
        service = DrinkService
        filters = subcat
        root_filter = {'description_ru': None}
        repository = DrinkRepository
        related_model_name = 'Subcategory'
        model = Drink
        result = await service.get_with_filter_complex(background_tasks, session, model,
                                                       related_model_name, repository,
                                                       filters, root_filter, 1, chunk, 0)
        items = result.get('items')
        if not items:
            #  остановка
            return None
        source: List = [(key.get('id'), key.get('description')) for key in items]
        payload['phrases'] = source
        """
        result: List[Dict]
        """
        result = await translation_service.translate_batch(source, payload.get('system_prompts'),
                                                           payload.get('user_prompts'),
                                                           payload.get('params'),
                                                           payload.get('lang'),
                                                           payload.get('drink'))
        jprint(result)
        trservice = TranslateRawDataService
        trrepo = TranslateRawDataRepository
        trmodel = TranslateRawData
        response = await trservice.create_bulk(result, trrepo, trmodel, session)
        return response


class TranslateRawDataService(Service):
    default = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']
