# app.suport.ollama.router.py
from typing import List, Optional
from loguru import logger
from fastapi import BackgroundTasks, Depends, Form, HTTPException, Query, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.enum import Categories, Preset, Prompts, Writers
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.core.utils.common_utils import compare_lists_compact, jprint
from app.support import Category
from app.support.category.repository import CategoryRepository
from app.support.ollama.model import Ollama, Prompt, ISOLanguage, Proption, WriterRule
from app.support.ollama.schemas import (LlmResponseSchema, OllamaCreate, PromptCreate,
                                        PromptRead, PromptUpdate, WriterRuleRead, WriterRuleCreate, WriterRuleUpdate,
                                        ISOLanguageCreate, ISOLanguageRead, ISOLanguageUpdate,
                                        ProptionRead, ProptionCreate, ProptionUpdate)
from app.support.ollama.service import LLMService, OllamaService

writter_prompt = """
Определи язык оригинала и переведи текст \"{phrase}\" на {lang} язык.
Данный текст относится к области \"{drink}\" - обязательно подбирай слова из соответствующего словаря,
используй устоявшийся эквивалент на {lang} языке.
Только при отсутствии эквивалента или подходящего словарного слова - транслитерируй.
Переводи строго, без пояснений.
Обращай внимание на согласование родов.
Жесткое условие для фактов: {translation_hints}.
Категорически запрещено писать вводные слова, вступление, здороваться, комментировать или объяснять свое решение,
выдумывать несуществующие сущности.
Твой ответ должен начинаться сразу с перевода. Перевод «
"""


class OllamaRouter(BaseRouter):
    """ языковые модели для OLLAMA"""

    def __init__(self):
        super().__init__(model=Ollama, prefix="/ollama")
        self.LLMservice = LLMService()
        self.service = OllamaService

    def setup_routes(self):
        self.router.add_api_route("/llm", self.get_models_list,
                                  methods=["GET"],
                                  response_model=List[LlmResponseSchema],
                                  openapi_extra={'x-request-schema': None})
        self.router.add_api_route("/llm/{model}", self.del_model, methods=['DELETE'])
        self.router.add_api_route("/translate", self.get_translate,
                                  methods=['POST'],
                                  openapi_extra={'x-request-schema': None})
        self.router.add_api_route("/novel", self.get_novel,
                                  methods=['POST'],
                                  openapi_extra={'x-request-schema': None})
        self.router.add_api_route("/full", self.get_full, methods=["GET"],
                                  response_model=self.nonpaginated_response,
                                  openapi_extra={'x-request-schema': None}
                                  )
        # super().setup_routes()

    async def del_model(self,
                        background_tasks: BackgroundTasks,
                        model_name: str = Query(..., description="Имя модели."),
                        session: AsyncSession = Depends(get_db)) -> bool:
        try:
            response: bool = await self.LLMservice.del_model(model_name)
            if response:
                await self.get_models_list(background_tasks, session)
            return response
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_models_list(self, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_db)):
        """
        получение списка загруженных моделей.
        сравнение с сохраненными данными в базе данных и обновление
        """
        try:
            response: List[dict] = await self.LLMservice.get_models_list()

            iter = 0
            while iter < 2:
                iter += 1
                #  валидирует исходные данные и возвращает плоский словарь
                result = [LlmResponseSchema.model_validate(key).model_dump() for key in response]
                result2 = await self.service.get_full(self.repo, self.model, session)
                result3 = (OllamaCreate(**key.to_dict()).model_dump() for key in result2)
                #  словарь с различиями added, removed, changed
                resp = compare_lists_compact(result3, result, 'model')
                if not resp:
                    return result
                # для remove <и changed> заменяем на id
                for key in ('removed', 'changed'):
                    if x := resp.get(key):
                        x = [b if key == 'removed' else (b, a)
                             for a in x for b in result2 if a['model'] == b.model]
                        resp[key] = x
                await self.service.maintain_llm_database(resp, self.repo, self.model, session)
            error = 'база данных ll моделей не может синхронизироваться с реально загруженными ll моделямии'
            logger.error(error)
            jprint(resp)
            raise Exception(error)
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_translate(self, phrase: str = Body(..., description="Текст для перевода.",
                                                     title="текст для перевода",
                                                     media_type="text/plain",),
                            llmodel: str = Query('translategemma:latest', description="Имя модели в базе данных"),
                            prompt: Prompts = Query('universal_translator', description="Имя промпта в базе данных"),
                            preset: Preset = Query(None, description="Типовые настройки качество/скорость"),
                            writer: Writers = Query(None, description="Типовые правила перевода"),
                            langs: str = Query('ru, en',
                                               description="Язык (языки) перевода двух-значные коды через "
                                                           "запятую, например 'ru, fr, zh'"),
                            session: AsyncSession = Depends(get_db)):
        """
           тестирование моделей для перевода:
           1. фраза для перевода
           2. модель LL выбирается наименьшая из всех с совпадающим именем
           3. prompt
           3. язык/языки для перевода
           возвращает:
        """
        try:
            result = await self.service.get_translate(phrase, llmodel, prompt, preset, writer, langs, session)
            return result
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)

    async def get_novel(
            self, phrase: str = Body(..., description="Наименование для описания.",
                                     title='введите тему для генерации текста',
                                     media_type="text/plain",),
            llmodel: str = Query('qwen3:8b', description="Имя модели в базе данных"),
            prompt: Prompts = Query(None, description="Имя промпта в базе данных"),
            preset: Preset = Query(None, description="Типовые настройки качество/скорость"),
            writer: Writers = Query(None, description="Типовые правила генерации текста"),
            langs: str = Query('ru, en',
                               description="Язык (языки) перевода двух-значные коды через запятую"),
            # langs: Languages = Query('ru', description="Язык текста 2-3 значный код"),
            verify: bool = Query(False, description='Верифицировать перевод или нет'),
            session: AsyncSession = Depends(get_db)
    ) -> List[dict]:
        """
           # тестирование моделей для генерации текста:
           ## 1. наименование для генерации описания
           ## 2. модель LL выбирается наименьшая из всех с совпадающим именем
           ## 3. prompt
        """
        try:
            result = await self.service.get_novel(phrase, llmodel, prompt, preset, writer, langs, verify, session)
            return result
        except Exception as e:
            raise HTTPException(status_code=501, detail=e)


class ISOLanguageRouter(BaseRouter):
    """ языки мира """

    def __init__(self):
        super().__init__(model=ISOLanguage, prefix="/isolanguage")

    def setup_routes(self):
        self.router.add_api_route(
            "/batch", self.batch_create, status_code=200, methods=['POST'],
            response_model=List[self.read_schema_relation],
            openapi_extra={'x-request-schema': f"List_{self.create_schema_relation.__name__}"}
        )
        super().setup_routes()

    async def create(self, data: ISOLanguageCreate, session: AsyncSession = Depends(get_db)) -> ISOLanguageRead:
        return await super().create(data, session)

    async def batch_create(self, data: List[ISOLanguageCreate],
                           session: AsyncSession = Depends(get_db)) -> List[ISOLanguageRead]:
        return await super().batch_create(data, session)

    async def patch(self, id: int, data: ISOLanguageUpdate,
                    background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)) -> ISOLanguageRead:
        return await super().patch(id, data, background_tasks, session)


class PromptRouter(BaseRouter):
    """ промты для llm """

    def __init__(self):
        super().__init__(model=Prompt, prefix="/prompt")
        self.LLMservice = LLMService()

    def setup_routes(self):
        super().setup_routes()

    async def create(self,
                     role: str = Form(..., description='роль'),
                     system_prompt: str = Form(..., description='промпт должен содержать {lang}'),
                     category: Categories = Form(..., description='категория к которой применен prompt'),
                     subcategory_ids: List[int] = Form(..., description='id субкатегорий'),
                     active: bool = Form(True, description='активировано'),
                     session: AsyncSession = Depends(get_db)) -> PromptRead:
        response = await CategoryRepository.get_by_field('name', category, Category, session)
        category_id = response.id
        data = PromptCreate(role=role, system_prompt=system_prompt, category_id=category_id, active=active)
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: PromptUpdate,
                    background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)) -> PromptRead:
        return await super().patch(id, data, background_tasks, session)

    async def update_or_create(self, data: PromptCreate,
                               background_tasks: BackgroundTasks,
                               session: AsyncSession = Depends(get_db)) -> PromptRead:
        return await super().update_or_create(data, background_tasks, session)

    async def get_generate(self, translate_it: str = Query(None, description='текст, который нужно перевести'),
                           session: AsyncSession = Depends(get_db)):
        """
            Перевод текста

        """
        return translate_it


class ProptionRouter(BaseRouter):
    def __init__(self):
        super().__init__(model=Proption, prefix="/proption")

    async def create(self,
                     preset: str = Form(..., description='уникальное название настройки'),
                     category: Categories = Form(..., description='категория к которой применен proption'),
                     temperature: float = Form(0.1, ge=0.0, le=2.0, description="Температура генерации..."),
                     top_p: float = Form(0.85, ge=0.0, le=1.0, description="Nucleus sampling..."),
                     top_k: int = Form(50, ge=0, le=200,
                                       description="Ограничение выборки K наиболее вероятных токенов..."
                                       ),
                     frequency_penalty: float = Form(
                         0.2, ge=-2.0, le=2.0, description="Штраф за повторение токенов..."),
                     presence_penalty: float = Form(
                         0.1, ge=-2.0, le=2.0, description="Штраф за повторение тем..."),
                     repeat_penalty: float = Form(
                         1.1, ge=-2.0, le=2.0, description="Экспоненциальный штраф за повторение..."
                     ),
                     max_tokens: int = Form(2048, ge=1, le=4096,
                                            description="Максимальное количество токенов..."),
                     seed: Optional[int] = Form(None, ge=0, le=2147483647,
                                                description="Сид для воспроизводимости..."),
                     min_p: float = Form(0.04, ge=0.0, le=1.0,
                                         description="Минимальная вероятность токена..."),
                     typical_p: float = Form(0.92, ge=0.0, le=1.0, description="Typical sampling..."),
                     stop: List[str] = Form(["<|im_end|>", "<|endoftext|>", "\n\n"],
                                            description="Стоп-последовательности."),
                     active: bool = Form(True, description='активировано'),
                     session: AsyncSession = Depends(get_db)
                     ) -> ProptionRead:

        # Преобразуем stop из строки в список (если строка не пуста)
        # stop_list = [s.strip() for s in stop.split(',') if s.strip()] if stop else []
        response = await CategoryRepository.get_by_field('name', category, Category, session)
        category_id = response.id
        data = ProptionCreate(preset=preset,
                              category_id=category_id,
                              temperature=temperature,
                              top_p=top_p, top_k=top_k, max_tokens=max_tokens, seed=seed,
                              frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
                              repeat_penalty=repeat_penalty, min_p=min_p, typical_p=typical_p,
                              stop=stop if stop else None,
                              active=active)
        return await super().create(data, session)

    async def patch(self, id: int, data: ProptionUpdate,
                    background_tasks: BackgroundTasks,
                    session: AsyncSession = Depends(get_db)) -> ProptionRead:
        return await super().patch(id, data, background_tasks, session)

    async def update_or_create(self, data: ProptionCreate,
                               background_tasks: BackgroundTasks,
                               session: AsyncSession = Depends(get_db)) -> ProptionRead:
        return await super().update_or_create(data, background_tasks, session)


class WriterRuleRouter(BaseRouter):
    def __init__(self):
        super().__init__(model=WriterRule, prefix="/writerrules")

    def setup_routes(self):
        self.setup_route_adv('create', 'get', 'search', 'get_one', 'patch', 'delete')

    async def create(self, request: Request,
                     prompt: str = Body(writter_prompt,
                                        description='промпт должен содержать пласхолдеры '
                                                    '{lang}, {prase}, {translation_hints}',
                                        media_type="text/plain"
                                        ),
                     name: str = Query(..., description='name'),
                     subcategory_ids: List[int] = Query(..., description='id субкатегорий'),
                     active: bool = Query(True, description='активировано'),
                     session: AsyncSession = Depends(get_db)
                     ):
        """
            ДОБАВЛЕНИЕ user_prompt В БАЗУ ДАННЫХ
        """
        if isinstance(subcategory_ids, str):
            subcat = set(subcategory_ids[0].split(','))
        else:
            subcat = None
        data = WriterRuleCreate(name=name, prompt=prompt, active=active, subcategory_ids=subcat)
        return await super().create(data, session)

    async def patch(self, request: Request,
                    prompt: str = Body(writter_prompt,
                                       description='промпт должен содержать пласхолдеры '
                                                   '{lang}, {prase}, {translation_hints}',
                                       media_type="text/plain"
                                       ),
                    name: Writers = Query(..., description='название - неизменяется'),
                    subcategory_ids: List[int] = Query(..., description='id субкатегорий'),
                    active: bool = Query(True, description='активировано'),
                    session: AsyncSession = Depends(get_db)
                    ):
        """
        ОБНОВЛЕНИЕ
        """
        pass
        # return await super().patch(id, data, background_tasks, session)
