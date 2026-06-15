# app.support.router.py
from typing import List, Optional

# app.suport.ollama.router.py
# from loguru import logger
from fastapi import BackgroundTasks, Depends, Form, HTTPException, Query, Body  # , BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enum import Preset, Prompts, Writers, Languages
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter, LightRouter
from app.core.services.translate_service import TranslationService
from app.dependencies import get_translation_service
from app.support.vllm.model import TranslateRawData
from app.support.vllm.schemas import TranslateRawDataCreate, TranslateRawDataUpdate
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
        self.router.add_api_route(
            "/translate3", self.get_translate_precise2, methods=["POST"],
            openapi_extra={'x-request-schema': None}
        )
        # super().setup_routes()

    async def get_translate(
            self, phrase: str = Body(
                ..., description="Текст для перевода.", title="текст для перевода",
                media_type="text/plain", ),
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

    async def get_translate_prompts(
        self,
        phrase: str = Form(...,
                           description="Текст для перевода."),
        prompt: Prompts = Form(..., description="системный prompt. Должен содержать ключевое слово {lang}"),
        proption: Preset = Form(None, description="Типовые настройки качество/скорость"),
        writer: Writers = Form(None, description="Типовые правила перевода. "
                               "Должны содержать ключевые слова {lang} и {phrase}"),
        langs: Languages = Form('ru',
                                description="Язык перевода"),
        subcategory: str = Form('wine', description='категория напитка'),
        session: AsyncSession = Depends(get_db),
        translation_service: TranslationService = Depends(get_translation_service)
    ):
        """
           тестирование промптов для перевода:
        """
        try:
            result = await self.VLLMservice.get_translate2(phrase,
                                                           prompt,
                                                           proption,
                                                           writer,
                                                           langs,
                                                           subcategory,
                                                           session,
                                                           translation_service,
                                                           )
            return result
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_translate_precise2(self,
                                     phrase: str = Form(..., description="Текст для перевода на английском языке."),
                                     prompt: str = Form(
                                         ..., description="Системный промпт. Должен содержать ключевое слово {lang} для подстановки языка."
                                     ),
                                     writer: Optional[str] = Form(
                                         None, description="Типовые правила перевода (предустановленные шаблоны промптов)."
                                     ), langs: str = Form(
                                         'ru',
                                         description="Язык перевода. Поддерживаются двух-значные коды... "
                                                     "Можно указать несколько через запятую: 'ru, fr, zh'"
                                     ),
                                     subcategory: str = Form('wine', description='категория напитка (красное вино, '
                                                                                 'абсент, ром ...)'),
                                     temperature: float = Form(0.1, ge=0.0, le=2.0, description="Температура генерации..."),
                                     top_p: float = Form(0.85, ge=0.0, le=1.0, description="Nucleus sampling..."), top_k: int = Form(
                                         50, ge=0, le=200, description="Ограничение выборки K наиболее вероятных токенов..."
                                     ),
                                     frequency_penalty: float = Form(
                                         0.2, ge=-2.0, le=2.0, description="Штраф за повторение токенов..."),
                                     presence_penalty: float = Form(
                                         0.1, ge=-2.0, le=2.0, description="Штраф за повторение тем..."),
                                     repeat_penalty: float = Form(
                                         1.1, ge=0.5, le=2.0, description="Экспоненциальный штраф за повторение..."
                                     ),
                                     max_tokens: int = Form(2048, ge=1, le=4096,
                                                            description="Максимальное количество токенов..."),
                                     seed: Optional[int] = Form(None, ge=0, le=2147483647,
                                                                description="Сид для воспроизводимости..."),
                                     min_p: float = Form(0.04, ge=0.0, le=1.0,
                                                         description="Минимальная вероятность токена..."),
                                     typical_p: float = Form(0.92, ge=0.0, le=1.0, description="Typical sampling..."), stop: str = Form(
                                         "",
                                         description="Стоп-последовательности. Укажите через запятую (без пробелов). Пример: '\\n\\n,.</s>'"
                                     ), translation_service: TranslationService = Depends(get_translation_service)
                                     ):
        """
            тестирование перевода - тонкие настройки
            Form применяется потому что query не вывозит размер данных
        """
        stop_list = [s.strip() for s in stop.split(',') if s.strip()] if stop else []

        result = await translation_service.translate(
            phrase=phrase, system_prompt=prompt, user_prompt=writer, lang_code=langs, drink=subcategory,
            temperature=temperature, top_p=top_p, top_k=top_k, max_tokens=max_tokens, seed=seed,
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
            repeat_penalty=repeat_penalty, min_p=min_p, typical_p=typical_p,
            stop=stop_list if stop_list else None
        )
        return result


class TranslateRawDataRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=TranslateRawData,
            prefix="/translaterawdata",
        )

    async def create(self, data: TranslateRawDataCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def patch(self, id: int, data: TranslateRawDataUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: TranslateRawDataCreate,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result
