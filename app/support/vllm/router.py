# app.support.router.py
from typing import List, Optional, Set

# app.suport.ollama.router.py
from loguru import logger
from fastapi import BackgroundTasks, Depends, Form, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enum import Preset, Prompts, Writers, Languages
from app.core.config.database.db_async import DatabaseManager, get_db
from app.core.routers.base import BaseRouter, LightRouter
from app.core.services.translate_service import TranslationService
from app.dependencies import get_translation_service
from app.support import DrinkService
from app.support.vllm.model import TranslateRawData
from app.support.vllm.schemas import TranslateRawDataCreate, TranslateRawDataUpdate
# from app.core.utils.common_utils import compare_lists_compact, jprint
# from app.support.ollama.model import Prompt, ISOLanguage, Proption, WriterRule
from app.support.vllm.service import VLLMService
from app.support.vllm.repository import TranslateRawDataRepository  # NOQA: F401


class VllmRouter(LightRouter):
    """ языковые модели для OLLAMA"""

    def __init__(self):
        super().__init__(prefix="/vllm")
        self.service = VLLMService()

    def setup_routes(self):
        self.router.add_api_route(
            "/translate2", self.get_translate_prompts, methods=["POST"],
            openapi_extra={'x-request-schema': None}
        )
        self.router.add_api_route(
            "/translate3", self.get_translate_precise2, methods=["POST"],
            openapi_extra={'x-request-schema': None}
        )
        self.router.add_api_route(
            "/bulk_test", self.bulk_test, methods=["GET"],
            openapi_extra={'x-request-schema': None}
        )
        self.router.add_api_route(
            "/adv_test", self.adv_test, methods=["POST"], openapi_extra={'x-request-schema': None}
        )
        # super().setup_routes()

    async def get_translate_prompts(
        self,
        phrase: str = Form(...,
                           description="Текст для перевода."),
        prompt: Prompts = Form(..., description="системный prompt. Должен содержать ключевое слово {lang}"),
        proption: Preset = Form(..., description="Типовые настройки качество/скорость"),
        writer: Writers = Form(..., description="Типовые правила перевода. "
                               "Должны содержать ключевые слова {lang} и {phrase}"),
        langs: Languages = Form(...,
                                description="Язык перевода"),
        subcategory: str = Form('wine', description='категория напитка'),
        session: AsyncSession = Depends(get_db),
        translation_service: TranslationService = Depends(get_translation_service)
    ):
        """
           тестирование промптов для перевода:
        """
        try:
            result = await self.service.get_translate2(phrase, prompt, proption,
                                                       writer, langs, subcategory,
                                                       session, translation_service,
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
                                     temperature: float = Form(
                                         0.1, ge=0.0, le=2.0, description="Температура генерации..."),
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

    async def bulk_test(self, background_tasks: BackgroundTasks,
                        session: AsyncSession = Depends(get_db),
                        translation_service: TranslationService = Depends(get_translation_service),
                        subcat: str = Query(..., description='значение субкатегории - либо id либо имя на анг (нужно '
                                                             'угадать)'),
                        chunk: int = Query(20, description='размер выборки для тестирования'),
                        lang: Languages = Query(..., description="Язык перевода")):
        """
            тестирование массового перевода background_tasks
        """
        await self.service.bulk_test(session_factory=DatabaseManager.session_maker,
                                     translation_service=translation_service,
                                     subcat=subcat,
                                     chunk=chunk,
                                     lang=lang.value,
                                     background_tasks=background_tasks)
        return {'result': 'Translation started in backgound taska'}

    async def adv_test(self, background_tasks: BackgroundTasks,
                       # session: AsyncSession = Depends(get_db),
                       translation_service: TranslationService = Depends(get_translation_service),
                       author: List[Prompts] = Query(...,
                                                     descrition='для выбора нескольких значений используй Alt'),
                       user_prompt: List[Writers] = Query(...,
                                                          descrition='для выбора нескольких значений используй Alt'),
                       params: List[Preset] = Query(...,
                                                    descrition='для выбора нескольких значений используй Alt'),
                       subcat: str = Query(...,
                                           description='id субкатегориии'),
                       chunk: int = Query(1, description='размер выборки для тестирования'),
                       lang: Languages = Query(..., description="Язык перевода")):
        """
            тестирование перевода:
            в зависимости от цели:
            - сравнить двух (или более) авторов: выбрать двух или более авторов, остальное в по одному
            - сравнить user_prompt: выбрать два или более user_prompt, остальное по одному
            и так далее
        """
        author = [item.value for item in author]
        user_prompt = [item.value for item in user_prompt]
        params = [item.value for item in params]
        await self.service.adv_test(
            session_factory=DatabaseManager.session_maker, translation_service=translation_service,
            author=author, user_prompt=user_prompt,
            param=params, subcat=subcat, chunk=chunk, lang=lang,
            background_tasks=background_tasks)
        return {'result': 'Translation started in backgound taska'}


class TranslateRawDataRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=TranslateRawData,
            prefix="/translaterawdata",
        )

    async def create(self, data: TranslateRawDataCreate,
                     session: AsyncSession = Depends(get_db)):
        from app.core.utils.common_utils import jprint
        print(type(data))
        jprint(data)
        return await super().create(data, session)

    async def patch(self, id: int, data: TranslateRawDataUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)

    async def create_relation(self, data: TranslateRawDataCreate,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result
