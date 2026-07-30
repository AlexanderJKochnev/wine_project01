# app.suport.ollama.router.py
from typing import List, Optional

from fastapi import BackgroundTasks, Body, Depends, Form, HTTPException, Query, Request
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.enum import Categories, Preset, Prompts, Writers
from app.core.routers.base import BaseRouter
from app.core.utils.common_utils import compare_lists_compact, jprint
from app.core.utils.pydantic_utils import inst_dict
from app.support import Category
from app.support.category.repository import CategoryRepository
from app.support.ollama.model import ISOLanguage, Ollama, Prompt, Proption, WriterRule
from app.support.ollama.repository import PromptRepository, WriterRuleRepository
from app.support.ollama.schemas import (ISOLanguageCreate, ISOLanguageRead, LlmResponseSchema, OllamaCreate,
                                        PromptCreate, ProptionCreate, ProptionRead, ProptionUpdate, WriterRuleCreate,
                                        WriterRuleUpdate)
from app.support.ollama.service import LLMService, OllamaService, PromptService, WriterRuleService

writter_prompt = """Определи язык оригинала и переведи текст \"{phrase}\" на {lang} язык.
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

system_prompt = """You are an expert wine writer and professional translator.
Your task is to translate the text.
Translated text must sound like natural, fluent, and elegant wine/spirit journalism
(e.g., in the style of Bunin, Maugham, or elite wine magazines).
Check for:
- Flawless grammar, proper gender/case agreements, and natural sentence structures.
- ABSOLUTE ZERO TOLERANCE for literal translation (calque).
Phrases like "fruit of the winery", "hits of pepper", "wine's body" translated literally must be heavily penalized.
- It must sound like it was originally written by a native {lang} writer, not a machine.
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


class PromptRouter(BaseRouter):
    """ промты для llm """

    def __init__(self):
        super().__init__(model=Prompt, prefix="/prompt")
        # self.LLMservice = LLMService()
        self.service = PromptService
        self.repo = PromptRepository
        self.model = Prompt

    def setup_routes(self):
        self.setup_route_adv('create', 'get', 'search', 'get_one', 'patch', 'delete')

    async def create(self,
                     system_prompt: str = Body(system_prompt, description='системный промпт должен содержать описание роли',
                                               media_type="text/plain"),
                     role: str = Query(..., description='роль'),
                     subcategory_ids: List[int] = Query(..., description='id субкатегорий'),
                     active: bool = Query(True, description='активировано'),
                     session: AsyncSession = Depends(get_db)):
        if subcategory_ids:
            subcategory_ids = list(set(subcategory_ids))
        data = PromptCreate(role=role, system_prompt=system_prompt, subcategory_ids=subcategory_ids, active=active)
        return await self.service.create(data, self.repo, self.model, session)

    async def patch(self,
                    system_prompt: str = Body(None, description='системный промпт должен содержать описание роли',
                                              media_type="text/plain"),
                    role: Prompts = Query(..., description='роль'),
                    subcategory_ids: List[int] = Query(None, description='id субкатегорий'),
                    active: bool = Query(True, description='активировано'),
                    session: AsyncSession = Depends(get_db)):
        """
        ОБНОВЛЕНИЕ
        """
        result: Prompt = await self.repo.get_by_field_v2({'role': role}, self.model, session)
        if subcategory_ids:
            subcategory_ids = list(set(subcategory_ids))
        if system_prompt == 'sting':
            system_prompt = None
        data: WriterRuleUpdate = self.update_schema(system_prompt=system_prompt,
                                                    subcategory_ids=subcategory_ids, active=active)
        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        response = await self.repo.patch(result, data_dict, session)
        return inst_dict(response.get('data'))


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

    async def update_or_create(self, data: ProptionCreate,
                               background_tasks: BackgroundTasks,
                               session: AsyncSession = Depends(get_db)) -> ProptionRead:
        return await super().update_or_create(data, background_tasks, session)


class WriterRuleRouter(BaseRouter):
    def __init__(self):
        super().__init__(model=WriterRule, prefix="/writerrules")
        self.service = WriterRuleService
        self.repo = WriterRuleRepository
        self.model = WriterRule

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
        if subcategory_ids:
            subcategory_ids = list(set(subcategory_ids))
        data = WriterRuleCreate(name=name, prompt=prompt, active=active, subcategory_ids=subcategory_ids)
        return await self.service.create(data, self.repo, self.model, session)

    async def patch(self, request: Request,
                    prompt: str = Body(None,
                                       description='промпт должен содержать пласхолдеры '
                                                   '{lang}, {prase}, {translation_hints}, '
                                                   'если этот параметр не меняется - удали значение по умолчанию'
                                                   '',
                                       media_type="text/plain"
                                       ),
                    name: Writers = Query(..., description='название - не изменяемый параметр'),
                    subcategory_ids: List[int] = Query(None, description='id субкатегорий'),
                    active: bool = Query(None, description='активировано'),
                    session: AsyncSession = Depends(get_db)
                    ):
        """
        ОБНОВЛЕНИЕ
        """
        result: WriterRule = await WriterRuleRepository.get_by_field_v2({'name': name}, WriterRule, session)
        if subcategory_ids:
            subcategory_ids = list(set(subcategory_ids))
        if prompt == 'sting':
            prompt = None
        data: WriterRuleUpdate = self.update_schema(prompt=prompt, subcategory_ids=subcategory_ids, active=active)
        data_dict = data.model_dump(exclude_unset=True, exclude_none=True)
        response = await self.repo.patch(result, data_dict, session)
        return inst_dict(response.get('data'))
