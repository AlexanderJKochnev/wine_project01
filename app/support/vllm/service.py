# app.support.vllm.service.py
import time
from typing import List

from fastapi import HTTPException
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
from app.core.services.translate_service import TranslationService
from app.core.types import ModelType
from app.core.utils.benchmarks import get_metrics
from app.core.utils.common_utils import clean_string
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

    async def get_datas(self, phrase: str, prompt: str, proption: str, writer: str, language: str,
                        session: AsyncSession):
        langs = [lang.strip() for lang in language.split(',')]
        lang_response: List[ISOLanguage] = await ISOLanguageRepository.search_by_list_value_exact(langs, 'iso_639_1', ISOLanguage,
                                                                                                  session)

        language_set = {lang.iso_639_1 for lang in lang_response}
        dataset = {'prompt': (Prompt, PromptRepository, 'role', 'system_prompt', prompt),
                   'writer': (WriterRule, WriterRuleRepository, 'name', 'prompt', writer),
                   'proption': (Proption, ProptionRepository, 'preset', None, proption)}
        payload: dict = {}
        for key, val in dataset.items():
            model, repo, field_name, field_out, search = val
            tmp: ModelType = await repo.get_by_field(field_name, search, model, session)
            if field_out:
                payload[key] = getattr(tmp, field_out)
            else:
                payload[key] = tmp.to_dict()
        result: dict = {}
        for lang in language_set:
            response = await self.performing(lang, phrase, payload)
            result[lang] = response  # .choices[0].message.content
        return result

    async def performing(self, lang: str, phrase: str, payload: dict):
        """
            перевод/генерация текста
        """
        try:
            start_ms = time.time() * 1000
            options = payload.get("proption", {})
            gpu_ms = time.time() * 1000
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": payload.get("prompt", "")},
                          # Маппинг параметров в формат OpenAI/vllm
                          {"role": "user", "content": payload.get("writer", "").format(lang=lang, phrase=phrase)}],
                temperature=options.get("temperature", 0.1), top_p=options.get("top_p", 0.1),
                max_tokens=options.get("num_predict", 1024), presence_penalty=options.get("presence_penalty", 0),
                frequency_penalty=options.get("frequency_penalty", 0), seed=options.get("seed", 42),
                stop=options.get("stop", None)
            )
            response = get_metrics(clean_string(response.choices[0].message.content),
                                   response.usage.completion_tokens,
                                   start_ms, gpu_ms
                                   )
            return response
            # return response.choices[0].message.content
        except Exception as x:
            logger.error(f'base_url "http://172.60.0.10/v1", error: {x}')
            return {'result': False}

    async def get_translate(self, phrase, prompt: str, proption: str, writer: str, langs: str,
                            session: AsyncSession,
                            **kwargs):
        # phrase, prompt, preset, writer, langs, session
        result = await self.get_datas(phrase, prompt, proption, writer, langs, session)
        return {'response': True if result else False, 'answer': result}

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

    async def get_lang(self, langs: str, session: AsyncSession):
        """
            получение одного языка для перевода
        """
        langs = [lang.strip() for lang in langs.split(',')]
        lang_response: List[ISOLanguage] = await ISOLanguageRepository.search_by_list_value_exact(langs, 'iso_639_1', ISOLanguage,
                                                                                                  session)
        if lang_response:
            return lang_response[0].name_en
        raise HTTPException(detail='language not found', status_code=404)

    async def get_payload(self, prompt: str, proption: str, writer: str,
                          session: AsyncSession):
        """
            формирование patyload для массового перевода
            prompt, writer - могцт быть как названием из базы данных так и собственно значением параметра
        """
        # язык перевода тут не задается (один язык - для массового перевода)
        dataset = {'prompt': (Prompt, PromptRepository, 'role', 'system_prompt', prompt),
                   'writer': (WriterRule, WriterRuleRepository, 'name', 'prompt', writer),
                   'proption': (Proption, ProptionRepository, 'preset', None, proption)}
        payload: dict = {}
        for key, val in dataset.items():
            model, repo, field_name, field_out, search = val
            # if '{lang}' in search:
            if key in ('prompt', 'writer'):
                payload[key] = search
            else:
                tmp: ModelType = await repo.get_by_field(field_name, search, model, session)
                if field_out:
                    payload[key] = getattr(tmp, field_out)
                else:
                    payload[key] = tmp.to_dict()
        return payload

    async def performing2(self, lang: str, phrase: str, payload: dict):
        """
        перевод/генерация текста
        """
        try:
            start_ms = time.time() * 1000
            options = payload.get("proption", {})
            gpu_ms = time.time() * 1000

            # Получаем компоненты из payload
            system_template = payload.get("prompt", "")
            system_content = system_template.format(lang=lang)
            user_template = payload.get("writer", "")
            user_content = user_template.format(lang=lang, phrase=phrase)

            # 🔥 КЛЮЧЕВОЕ ИЗМЕНЕНИЕ: Форматируем в стиле Mistral
            # Формат: [INST] {system_prompt}\n\n{user_message} [/INST]
            formatted_prompt = f"[INST] {system_content}\n\n{user_content} [/INST]"
            print(f'{formatted_prompt=}')

            # Для Mistral токенизатора используем completions endpoint (не chat.completions)
            response = await self.client.completions.create(
                model=self.model_name, prompt=formatted_prompt, temperature=options.get("temperature", 0.1),
                top_p=options.get("top_p", 0.9), max_tokens=options.get("num_predict", 1024),
                frequency_penalty=options.get("frequency_penalty", 0),
                presence_penalty=options.get("presence_penalty", 0), seed=options.get("seed", 42),
                stop=options.get("stop", None)
            )

            response_text = clean_string(response.choices[0].text)
            response = get_metrics(
                response_text, response.usage.completion_tokens, start_ms, gpu_ms
            )
            response.update(options)
            return response

        except Exception as x:
            logger.error(f'base_url "http://172.60.0.10/v1", error: {x}')
            return {'result': False}


class TranslateRawDataService(Service):
    defaault = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']