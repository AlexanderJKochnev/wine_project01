# app.support.router.py
from typing import List, Optional, Set

# app.suport.ollama.router.py
from fastapi import BackgroundTasks, Depends, Form, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import DatabaseManager, get_db
from app.core.routers.mixin_router import ArrayRouter
from app.core.utils.common_utils import jprint
from app.support.vllm.dataclasses import DrinkTranslateData, HandbookTranslateData
from app.core.enum import Drinkfield, Handbooks, Languages, Preset, Prompts, Writers
from app.core.routers.base import BaseRouter, LightRouter
from app.core.services.translate_service import TranslationService
from app.dependencies import get_translation_service
from app.support.vllm.model import TranslateHelper, TranslateRawData
from app.support.vllm.repository import TranslateRawDataRepository  # NOQA: F401
from app.support.vllm.schemas import TranslateHelperCreate, TranslateHelperUpdate, TranslateRawDataCreate, \
    TranslateRawDataUpdate
# from app.core.utils.common_utils import compare_lists_compact, jprint
# from app.support.ollama.model import Prompt, ISOLanguage, Proption, WriterRule
from app.support.vllm.service import VLLMService


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
        self.router.add_api_route(
            "/handbooks_translate", self.handbook_translate, methods=["POST"], openapi_extra={'x-request-schema': None}
        )
        self.router.add_api_route(
            "/drink_translate", self.drink_translate, methods=["POST"], openapi_extra={'x-request-schema': None}
        )
        self.router.add_api_route(
            "/test", self.test, methods=['GET'], openapi_extra={'x-request-schema': None}
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
                                     ),
                                     lang: Languages = Form(..., description="Язык перевода. Выбрать из списка"
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
                                     typical_p: float = Form(0.92, ge=0.0, le=1.0, description="Typical sampling..."),
                                     translation_service: TranslationService = Depends(get_translation_service)
                                     ):
        """
            тестирование перевода - тонкие настройки
            Form применяется потому что query не вывозит размер данных
        """

        result = await translation_service.translate(
            phrase=phrase, system_prompt=prompt, user_prompt=writer, lang=lang, drink=subcategory,
            temperature=temperature, top_p=top_p, top_k=top_k, max_tokens=max_tokens, seed=seed,
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
            repeat_penalty=repeat_penalty, min_p=min_p, typical_p=typical_p,
            stop=["<|im_end|>", "<|endoftext|>", "\n\n"]
        )
        return result

    async def bulk_test(self, background_tasks: BackgroundTasks,
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
                       author: List[Prompts] = Form(...,
                                                    descrition='для выбора нескольких значений используй Alt'),
                       user_prompt: List[Writers] = Form(...,
                                                         descrition='для выбора нескольких значений используй Alt'),
                       params: List[Preset] = Form(...,
                                                   descrition='для выбора нескольких значений используй Alt'),
                       subcat: str = Form(...,
                                          description='id субкатегориии'),
                       chunk: int = Form(1, description='размер выборки для тестирования'),
                       lang: Languages = Form(..., description="Язык перевода")):
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
            param=params, subcat=subcat, chunk=chunk, lang=lang.value,
            background_tasks=background_tasks)
        return {'result': 'Translation started in backgound taska'}

    async def handbook_translate(
            self, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_db),
            translation_service: TranslationService = Depends(get_translation_service),
            handbook: Handbooks = Query(..., description='справочник'),
            language_origin: Languages = Query(..., description='язык оригинала'),
            language_destination: Languages = Query(..., description='язык оригинала'),
            author: Prompts = Query(
                ..., descrition='переводчик'
            ),
            user_prompt: Writers = Query(
                ..., descrition='промпт'
            ),
            params: Preset = Query(
                ..., descrition='настройки'
            ),
            chunk: int = Query(25, description='чанк'),
            score_threshold: int = Query(10, ge=1, le=10, description='нижний порог приемлемой оценки')
    ):
        """
            перевод справочников
        """
        data = await HandbookTranslateData.load_from_db(
            system=author,
            language_origin1=language_origin.value,
            language_destination1=language_destination.value,
            user=user_prompt,
            proption=params,
            chunk1=chunk,
            field='name',
            handbook1=handbook.value,
            score=score_threshold,
            session=session)
        response = await self.service.handbook_translate(session_factory=DatabaseManager.session_maker,
                                                         translation_service=translation_service,
                                                         dataclass=data, background_tasks=background_tasks
                                                         )
        return response

    async def test(self, session: AsyncSession = Depends(get_db)):
        stats = await self.service.__stats__(session)
        await self.service.__del_bad_scores__(stats, session)
        result = await self.service.__update_handbook__(stats, session)
        await self.service.__clear_tmptable__(session)
        await session.commit()
        session.expire_all()
        return result

    async def drink_translate(self, background_tasks: BackgroundTasks,
                              session: AsyncSession = Depends(get_db),
                              translation_service: TranslationService = Depends(get_translation_service),
                              user_prompt: Writers = Query(..., descrition='промпт'),
                              author: Prompts = Query(..., descrition='переводчик'),
                              params: Preset = Query(..., descrition='настройки'),
                              language_origin: Languages = Query(..., description='язык оригинала'),
                              language_destination: Languages = Query(..., description='язык оригинала'),
                              chunk: int = Query(25, description='чанк'),
                              fieldname: Drinkfield = Query('description', description='имя переводимого поля'),
                              score_threshold: int = Query(8, ge=1, le=10, description='нижний порог приемлемой '
                                                           'оценки')
                              ):
        """
            сервис массового перевода описаний
            user_prompt привязан к подкатегориям
        """
        data = await DrinkTranslateData.load_from_db(system=author,
                                                     language_origin1=language_origin.value,
                                                     language_destination1=language_destination.value,
                                                     user=user_prompt,
                                                     proption=params,
                                                     chunk1=chunk,
                                                     field=fieldname.value,
                                                     score=score_threshold,
                                                     session=session)
        await self.service.drink_translate(session_factory=DatabaseManager.session_maker,
                                           translation_service=translation_service,
                                           data=data,
                                           background_tasks=background_tasks)
        return {'result': 'backgound process running'}


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


class TranslateHelperRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=TranslateHelper,
            prefix="/translatehelper",
        )
        self.arrayName: str = 'drow'

    def setup_routes(self):
        self.router.add_api_route(
            "/create", self.create,
            methods=["POST"],
            openapi_extra={'x-request-schema': None}
        )

    async def create(self,
                     word: str = Form(..., description='слово или фраза'),
                     translate: List[str] = Form(..., description='предпочитаемый перевод'),
                     replace: bool = Form(False, description='True - мусор для замены перед переводом, '
                                          'False - подсказка переводчику'),
                     session: AsyncSession = Depends(get_db)):
        drow = set(translate)
        data = TranslateHelperCreate(word=word, drow=set(translate), shit=replace)
        return await super().create(data, session)

    async def patch(self, id: int, data: TranslateHelperUpdate, background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)):
        return await super().patch(id, data, background_tasks, session)
