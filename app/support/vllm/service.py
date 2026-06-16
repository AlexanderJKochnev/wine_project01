# app.support.vllm.service.py
from fastapi import BackgroundTasks
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
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
    4. запрос/ответ
    5. encoding
    ПРОВЕРИТЬ - ТОЛЬКО TRANSLATE2 использеется остальнео deprecated
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
                   'lang': (ISOLanguage, ISOLanguageRepository, 'iso_639_1', 'name_en', lang)
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
                        subcat: str):
        """
        тестирование
        """
        logger.warning('2---------------')
        service = DrinkService
        filters = {'name': subcat}
        repository = DrinkRepository
        related_model_name = 'Subcategory'
        model = Drink
        logger.warning('3---------------')
        result = await service.get_with_filter_simple(background_tasks, session, model,
                                                      related_model_name, repository,
                                                      filters, 1, 20, 0)
        return result


class TranslateRawDataService(Service):
    defaault = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']