# app.support.vllm.service.py
import time
from typing import List, Sequence, Tuple

from sqlalchemy import text
from sqlalchemy.dialects import postgresql

from app.core.enum import HANDBOOKS
from app.core.utils.backgound_tasks import background_unique
from app.core.utils.common_utils import jprint
from fastapi import HTTPException  # , BackgroundTasks,
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
from app.support.ollama.model import ISOLanguage, Prompt, Proption, WriterRule
from app.support.ollama.repository import ISOLanguageRepository, PromptRepository, ProptionRepository, \
    WriterRuleRepository
from app.support.subcategory.repository import SubcategoryRepository
from app.support.vllm.model import TmpTranslate
from app.support.vllm.repository import TmpTranslateRepository, TranslateRawDataRepository
from app.core.config.project_config import settings


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
        self.model_name = "/model"

    @staticmethod
    def get_subcat_filter(subcat: str) -> dict | list:
        if subcat.isnumeric():
            filters = {'id': int(subcat)}
        else:
            try:
                filters = tuple(int(item.strip()) for item in subcat.split(','))
            except Exception:
                filters = {'name': subcat}
        return filters

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

    @background_unique
    async def bulk_test(self, session_factory, translation_service: TranslationService,
                        subcat: str, chunk: int, lang: str):
        """
            это тестирование качества перевода
            по катерогриям/субкатегориям напитков
            по результатам тестирования будут выбраны лучшие авторы для каждой субкатегории напитков
            поэтому сейчас их привязка к категориям не учитывается
        """
        # список данных для перевода

        subcat_dict = self.get_subcat_filter(subcat)
        language: str = lang
        logger.info('run bulk_test in background')
        start_time = time.time()
        # запуск сессии
        async with session_factory() as session:
            # наименовние подкатегории напитка
            drink: str = await self.get_subcategiory(subcat_dict, session)
            system_prompts: List[Tuple] = await self.get_system_prompts(session)
            user_prompts: List[Tuple] = await self.get_user_prompts(session)
            params: List[dict] = await self.get_proptions(session)
            """
            payload = {'system_prompts': system_prompts,
                       'user_prompts': user_prompts,
                       'lang': language,
                       'drink': drink,
                       'params': params}
            """
            data: List = await self.get_data(session, subcat_dict, chunk)
            await session.commit()
        # запуск перевода
        result = await translation_service.translate_batch(
            data, system_prompts, user_prompts, params,
            language, drink
        )
        # запуск второй сессии
        async with session_factory() as session:
            trservice = TranslateRawDataService
            trrepo = TranslateRawDataRepository
            trmodel = TranslateRawData
            await trservice.create_bulk(result, trrepo, trmodel, session)
            await session.commit()
        duration_s = time.time() - start_time
        logger.info(f'bulk_test in background finished. total duration is {duration_s}')

    @staticmethod
    async def get_system_prompts(session: AsyncSession, values: List[str] = None) -> Sequence[tuple]:
        """
            получение списка промптов
        """
        model, repo = Prompt, PromptRepository
        if values:
            response: Sequence[Prompt] = await repo.get_by_field_values(model=model, session=session, field_name='role',
                                                                        values=values)
        else:
            filter = {'active': True}
            response: Sequence[Prompt] = await repo.get_list_by_field_v2(filter=filter, model=model, session=session)
        if response:
            return [(inst.id, inst.system_prompt, inst.role) for inst in response]

    @staticmethod
    async def get_system_prompt(session: AsyncSession, value: str) -> tuple:
        """
            получение одного системного промпта
        """
        model, repo = Prompt, PromptRepository
        result: Prompt = await repo.get_by_field_v2({'role': value}, model, session)
        return result.id, result.system_prompt, result.role

    @staticmethod
    async def get_user_prompt(session: AsyncSession, value: str) -> Tuple:
        """
            получение одного user_prompt
        """
        model, repo = WriterRule, WriterRuleRepository
        result: WriterRule = await repo.get_by_field_v2({'name': value}, model, session)
        return result.id, result.prompt, result.name

    @staticmethod
    async def get_user_prompts(session: AsyncSession, values: List[str] = None) -> Sequence[tuple]:
        """
            получение списка промптов
        """
        model, repo = WriterRule, WriterRuleRepository
        if values:
            response: Sequence[WriterRule] = await repo.get_by_field_values(model=model, session=session,
                                                                            field_name='name',
                                                                            values=values)
        else:
            filter = {'active': True}
            response: List[WriterRule] = await repo.get_list_by_field_v2(filter=filter, model=model, session=session)
        if response:
            return [(inst.id, inst.prompt, inst.name) for inst in response]

    @staticmethod
    async def get_proption(session: AsyncSession, value: str) -> dict:
        """
            получение одного proption
        """
        model, repo = Proption, ProptionRepository
        result: Proption = await repo.get_by_field_v2({'preset': value}, model, session)
        return inst_dict(result)

    @staticmethod
    async def get_proptions(session: AsyncSession, values: List[str] = None) -> Sequence[dict]:
        """
            получение списка настроек
        """
        model, repo = Proption, ProptionRepository
        if values:
            response: Sequence[WriterRule] = await repo.get_by_field_values(model=model, session=session,
                                                                            field_name='preset',
                                                                            values=values)
        else:
            filter = {'active': True}
            response: Sequence[WriterRule] = await repo.get_list_by_field_v2(filter=filter, model=model, session=session)
        if response:
            return list_dict(response)

    @staticmethod
    async def get_lang(filters: dict, session: AsyncSession) -> str:
        """
            получение суффикса 2-х символьного кода языка
        """
        model, repo = ISOLanguage, ISOLanguageRepository
        response: ISOLanguage = await repo.get_by_field_v2(filters, model, session)
        default_lang: str = settings.DEFAULT_LANG
        lang: str = response.iso_639_1
        return '' if lang == default_lang else f'_{lang}'

    @staticmethod
    async def get_subcategiory(filters: dict | tuple, session: AsyncSession) -> str:
        """
        получение субкатегории на языке перевода
        пока на одну субкатегорию и русский язык
        нужно будет додедлать под несколько субкат и язык промпта
        """
        model, repo = Subcategory, SubcategoryRepository
        response: Subcategory = await repo.get_by_field_v2(filters, model, session)
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
                       session: AsyncSession,
                       subcat: dict,
                       chunk: int  # размер тестовой выборки
                       ) -> List[Tuple]:
        service = DrinkService
        filters = subcat
        root_filter = {'description_ru': None}
        repository = DrinkRepository
        related_model_name = 'Subcategory'
        model = Drink
        try:
            result = await service.get_with_filter_complex(session, model,
                                                           related_model_name, repository,
                                                           filters, root_filter, 1, chunk, 0)
            items = result.get('items')
            source: List = [(key.get('id'), key.get('description')) for key in items]
        except Exception as e:
            raise HTTPException(status_code=404, detail=f'No records suitable. {e}')
        return source

    @background_unique
    async def adv_test(self, session_factory, translation_service: TranslationService,
                       author: List[str],
                       user_prompt: List[str],
                       param: List[str],
                       subcat: str,
                       chunk: int,
                       lang: str):
        """
        тестирование функции перевода
        """
        # получение отфильтрованных списков

        subcat_dict = self.get_subcat_filter(subcat)
        language: str = lang
        logger.info('run bulk_test in background')
        start_time = time.time()
        # запуск сессии
        async with session_factory() as session:
            # словесное обозначение субкатегории
            data: List = await self.get_data(session, subcat_dict, chunk)
            drink: str = await self.get_subcategiory(subcat_dict, session)
            system_prompts: Sequence[Tuple] = await self.get_system_prompts(session, author)
            user_prompts: Sequence[Tuple] = await self.get_user_prompts(session, user_prompt)
            params: Sequence[dict] = await self.get_proptions(session, param)
            await session.commit()  # запуск перевода
        result = await translation_service.translate_batch(
            data, system_prompts, user_prompts, params, language, drink
        )
        distill = [(v.get('drink_id'), v.get('origin'), v.get('result')) for v in result]
        # экспертная оценка
        evaluated: List[dict] = await translation_service.evaluate_translations_batch(result)
        logger.warning(evaluated)
        jprint(evaluated)
        # best_configs = translation_service.rank_translation_configs(evaluated)
        best_configs = translation_service.rank_translation_configs_v2(evaluated)
        for best_config in best_configs:
            best_config['prompt'] = next((item[2]
                                          for item in system_prompts
                                          if item[0] == best_config.get('prompt_id')), None)
            best_config['writerrule'] = next((item[2]
                                              for item in user_prompts
                                              if item[0] == best_config.get('writerrule_id')), None)
            best_config['proption'] = next((item.get('preset')
                                            for item in params
                                            if item.get('id') == best_config.get('proption_id')), None)
            best_config['result'] = (f"{best_config.get('prompt')} & {best_config.get('writerrule')}: "
                                     f"avg_score = {best_config.get('avg_score')} / "
                                     f"min/max = {best_config.get('min_score')} / {best_config.get('max_score')}")
            logger.info(best_config['result'])
        """
        'prompt_id': 24,
         'writerrule_id': 13,
         'proption_id': 6,
         'avg_score': 7.0,
         'min_score': 7.0,
         'max_score': 7.0,
         'total_phrases': 1,
         'prompt': 'Маркес',
         'writerrule': 'Wine',
         'proption': 'wine_warm'
            }
        """
        best_config = best_configs[0]
        logger.info(f"Лучший конфиг: {best_config}")
        drink_ids = set(a for a, b, c in distill)
        for id in drink_ids:
            top_translations = translation_service.get_best_translations_for_phrase(evaluated, drink_id=id)
            best_result_text = top_translations[0]['result']  # Текст для подстановки в базу
            logger.warning(f'{id}: {best_result_text}')
        # запуск второй сессии
        duration_s = time.time() - start_time
        logger.info(f'bulk_test in background finished. total duration is {duration_s}')
        return
        """
        async with session_factory() as session:

            trservice = TranslateRawDataService
            trrepo = TranslateRawDataRepository
            trmodel = TranslateRawData
            await trservice.create_bulk(result, trrepo, trmodel, session)
            await session.commit()
        duration_s = time.time() - start_time
        logger.info(f'bulk_test in background finished. total duration is {duration_s}')
        """

    @background_unique
    async def handbook_translate(self, session_factory, translation_service: TranslationService,
                                 handbook: str,
                                 system_prompt: str,
                                 language_origin: str,
                                 language_destination: str,
                                 user_prompt: str,
                                 params: str,
                                 chunk: int
                                 ):
        """
            перевод справочников
            0. язык двух символьный код
            1. получаем prompts
            2. определяем поля для источника и поля для перевода
            3. отфильтровываем и получаем (id, value in name_{lang}) where name_{dest} is null
            4. отправляем на перевод
            5. получаеv -> передаем на сохранение (update)
        """
        async with session_factory() as session:
            # 0.
            origin: str = await self.get_lang({'name_en': language_origin}, session)
            dest: str = await self.get_lang({'name_en': language_destination}, session)
            # 1.
            system_prompt: tuple = await self.get_system_prompt(session, system_prompt)
            user_prompt: tuple = await self.get_user_prompt(session, user_prompt)
            param: dict = await self.get_proption(session, params)
            # 2.
            source_field, target_field = f'name{origin}', f'name{dest}'
            session.commit
        tmp_model = TmpTranslate
        tmp_repo = TmpTranslateRepository
        last_id = 0
        descr = HANDBOOKS.get(handbook)
        while True:  # бесконечый цикл пока есть записи handbooks
            # 3. get data
            async with session_factory() as session:
                data, last_id = await self.fetch_data_chunk(session, source_field, target_field, handbook, chunk,
                                                            last_id)
                await session.commit()
            # 4. translate
            result = await translation_service.real_batch(
                data, system_prompt, user_prompt,
                param, language_destination, descr  # subj
            )
            # distill = [(v.get('drink_id'), v.get('origin'), v.get('result')) for v in result]
            # 5. save to temporary file
            # 5.0. ready to save
            distill = self.tmp_data_validate(result, handbook, target_field, dest)
            async with session_factory() as session:
                response = await tmp_repo.bulk_create(distill, tmp_model, session)
                result_dict = list_dict(response)
                jprint(result_dict)
                session.commit()
            logger.warning('--------')
            if not last_id:
                break
            # logger.warning(f'{system_prompt=}, \n\n {user_prompt=}, \n\n {source_field=}, \n\n {target_field=}, '
            #                f'{handbook=}, \n\n {params}')
        return None

    async def fetch_data_chunk(self, session: AsyncSession, source_field: str, target_field: str,
                               handbook: str, chunk: int, last_id: int = 0) -> tuple:
        """
        получение данных
        """
        raw_sql = """
        SELECT id, {origin} FROM {handbook}
        WHERE COALESCE({dest},'') = '' AND COALESCE({origin}, '') != ''
        AND id > {last_id}
        ORDER BY id
        LIMIT {chunk};
        """
        sql = raw_sql.format(origin=source_field, dest=target_field, handbook=handbook, last_id=last_id, chunk=chunk)
        stmt = text(sql)
        result = await session.execute(stmt)
        rows = result.all()
        result = tuple((row.id, row._mapping[source_field]) for row in rows)
        if len(result) < chunk:
            last_id = None
        else:
            last_id = result[-1][0]
        return result, last_id

    def tmp_data_validate(self, data: dict, handbook: str, target_field: str, language_destination) -> dict:
        """
            преобразование и валидация данных для добалвения во временную таблицу
            return:
            guid: int   id записи
            table: str  имя таблицы
            field: str  имя поля
            lang: str
            origin: str оригинал
            translate: str перевод
        """
        distill = [{'guid': v.get('drink_id'),
                    'table': handbook,
                    'field': target_field,
                    'lang': language_destination,
                    'origin': v.get('origin'),
                    'translate': v.get('result')} for v in data]
        return distill


class TranslateRawDataService(Service):
    default = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']


class TmpTranslateService(Service):
    default = ['id', 'table', 'field']
