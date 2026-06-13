# app.support.router.py
from typing import List

# app.suport.ollama.router.py
# from loguru import logger
from fastapi import Depends, Form, HTTPException, Query, Body  # , BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enum import Preset, Prompts, Writers  # , LLmodel, Languages, Writers
from app.core.config.database.db_async import get_db
from app.core.routers.base import LightRouter
from app.core.services.translate_service import TranslationServiceAdapter
from app.dependencies import get_translation_service
# from app.core.utils.common_utils import compare_lists_compact, jprint
# from app.support.ollama.model import Prompt, ISOLanguage, Proption, WriterRule
from app.support.vllm.service import VLLMService


class VllmRouter(LightRouter):
    """ языковые модели для OLLAMA"""

    def __init__(self):
        super().__init__(prefix="/vllm")
        self.VLLMservice = VLLMService()
        # self.service = VLLMService

    def setup_routes(self):
        self.router.add_api_route("/translate", self.get_translate,
                                  methods=["POST"],
                                  # response_model=List[LlmResponseSchema],
                                  openapi_extra={'x-request-schema': None})
        self.router.add_api_route(
            "/translate2", self.get_translate_prompts, methods=["POST"],
            openapi_extra={'x-request-schema': None}
        )
        # super().setup_routes()

    async def get_translate(
            self, phrase: str = Body(
                ..., description="Текст для перевода.", title="текст для перевода",
                media_type="text/plain", ),
            # llmodel: LLmodel = Query('translategemma:latest', description="Имя модели в базе данных"),
            prompt: Prompts = Query('universal_translator', description="Имя промпта в базе данных"),
            proption: Preset = Query(None, description="Типовые настройки качество/скорость"),
            writer: Writers = Query(None, description="Типовые правила перевода"),
            langs: str = Query(
                'ru, en', description="Язык (языки) перевода двух-значные коды через "
                "запятую, например 'ru, fr, zh'"
            ), session: AsyncSession = Depends(get_db)
    ):
        """
           тестирование моделей для перевода:
           1. фраза для перевода
           2. prompt
           3. язык/языки для перевода
           возвращает:
        """
        try:
            result = await self.VLLMservice.get_translate(phrase, prompt, proption, writer, langs, session)
            return result
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_translate_prompt(
            self, phrase: str = Body(
                ..., description="Текст для перевода.", title="текст для перевода",
                media_type="text/plain", ),
            prompt: str = Body(..., description="системный prompt. Должен содержать ключевое слово {lang}"),
            proption: Preset = Query(None, description="Типовые настройки качество/скорость"),
            writer: Writers = Query(None, description="Типовые правила перевода"),
            langs: str = Query(
                'ru', description="Язык (языки) перевода двух-значные коды через "
                "запятую, например 'ru, fr, zh'"
            ),
            # temperature:
            session: AsyncSession = Depends(get_db)
    ):
        """
           тестирование prompts (роли) для перевода:
           1. фраза для перевода
           2. prompt
           3. язык/языки для перевода
           возвращает:
        """
        try:
            result = await self.VLLMservice.get_translate2(phrase, prompt, proption, writer, langs, session)
            return result
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_translate_prompts(
        self,
        phrase: str = Form(...,
                           description="Текст для перевода."),
        prompt: str = Form(..., description="системный prompt. Должен содержать ключевое слово {lang}"),
        proption: Preset = Form(None, description="Типовые настройки качество/скорость"),
        writer: str = Form(None, description="Типовые правила перевода. "
                                             "Должны содержать ключевые слова {lang} и {phrase}"),
        langs: str = Form('ru, en',
                          description="Язык (языки) перевода двух-значные коды через "
                                      "запятую, например 'ru, fr, zh'"),
        session: AsyncSession = Depends(get_db)
    ):
        """
           тестирование prompts (роли) для перевода:
        """
        try:
            result = await self.VLLMservice.get_translate2(phrase,
                                                           prompt,
                                                           proption,
                                                           writer,
                                                           langs, session)
            return result
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_translate_precise(self,
                                    phrase: str = Body(
                                        ..., description="Текст для перевода на английском языке.", media_type="text/plain", ),
                                    prompt: str = Body(
                                        ..., description="Системный промпт. Должен содержать ключевое слово {lang} для подстановки языка."
                                    ),
                                    writer: Writers = Query(
                                        None, description="Типовые правила перевода (предустановленные шаблоны промптов)."
                                    ),
                                    langs: str = Query(
                                        'ru', description="Язык перевода. Поддерживаются двух-значные коды (ru, en, de, fr, es, it, zh, ja). "
                                        "Можно указать несколько через запятую: 'ru, fr, zh'"
                                    ),
                                    temperature: float = Query(
                                        0.1, ge=0.0, le=2.0,
                                        description="Температура генерации (0.0 - 2.0). Контролирует случайность ответа. "
                                        "0.0 = детерминированный режим (всегда самый вероятный токен). "
                                        "0.1-0.3 = рекомендуется для перевода и фактов. "
                                        "0.7-1.0 = для творческих задач. "
                                        "Чем выше значение, тем разнообразнее, но менее точный результат."
                                    ),
                                    top_p: float = Query(
                                        0.85, ge=0.0, le=1.0,
                                        description="Nucleus sampling (0.0 - 1.0). Ограничивает выбор токенов кумулятивной вероятностью. "
                                        "0.85-0.95 = рекомендуется для перевода. "
                                        "1.0 = отключен (все токены). "
                                        "Чем ниже значение, тем более предсказуемый результат."
                                    ),
                                    top_k: int = Query(
                                        50, ge=0, le=200, description="Ограничение выборки K наиболее вероятных токенов (0 - 200). "
                                        "0 = отключен. "
                                        "30-60 = рекомендуется для перевода. "
                                        "Чем ниже значение, тем точнее, но менее разнообразно."
                                    ),
                                    frequency_penalty: float = Query(
                                        0.2, ge=-2.0, le=2.0,
                                        description="Штраф за повторение токенов (-2.0 - 2.0). Учитывает частоту встречаемости токена в выводе. "
                                        "0.1-0.3 = рекомендуется для перевода (убирает повторы слов). "
                                        "Отрицательные значения поощряют повторения."
                                    ),
                                    presence_penalty: float = Query(
                                        0.1, ge=-2.0, le=2.0,
                                        description="Штраф за повторение тем (-2.0 - 2.0). Учитывает факт присутствия токена (бинарно). "
                                        "0.05-0.15 = рекомендуется для перевода. "
                                        "Помогает разнообразить лексику в длинных текстах."
                                    ),
                                    repeat_penalty: float = Query(
                                        1.1, ge=0.5, le=2.0,
                                        description="Экспоненциальный штраф за повторение токенов в контексте (0.5 - 2.0). "
                                        "1.05-1.15 = рекомендуется для перевода. "
                                        "1.0 = отключен. "
                                        "Чем выше значение, тем сильнее подавление повторов."
                                    ),
                                    max_tokens: int = Query(
                                        2048, ge=1, le=4096, description="Максимальное количество токенов в ответе (1 - 4096). "
                                        "Для дегустационных заметок достаточно 1024-2048."
                                    ),
                                    seed: int = Query(
                                        None, ge=0, le=2147483647,
                                        description="Сид для воспроизводимости результатов. При temperature=0 не влияет."
                                    ),
                                    min_p: float = Query(
                                        0.04, ge=0.0, le=1.0,
                                        description="Минимальная вероятность токена относительно max_probability (0.0 - 1.0). "
                                        "0.0 = отключен. 0.02-0.05 = рекомендуется. "
                                        "Отсекает очень маловероятные токены."
                                    ),
                                    typical_p: float = Query(
                                        0.92, ge=0.0, le=1.0, description="Typical sampling (0.0 - 1.0). Отбрасывает 'нетипичные' токены. "
                                        "0.9-0.95 = рекомендуется. 1.0 = отключен. "
                                        "Альтернатива top_p для плавного отсечения."
                                    ),
                                    stop: List[str] = Query(
                                        [], description="Стоп-последовательности. Генерация останавливается при появлении любой из строк. "
                                        'Пример: ["\\n\\n", ".</s>"]'
                                    ),
                                    translation_service: TranslationServiceAdapter = Depends(get_translation_service)
                                    # session: AsyncSession = Depends(get_db)
                                    ):
        """
             подбор параметров перевода
        """
