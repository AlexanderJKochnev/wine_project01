# app.support.vllm.service.py
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

from fastapi import HTTPException  # , BackgroundTasks,
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.project_config import settings
from app.core.services.array_service import ArrayService
from app.core.services.service import Service
from app.core.services.translate_service import TranslationService
from app.core.types import ModelType
from app.core.utils.alchemy_utils import get_model_by_tablename
from app.core.utils.backgound_tasks import background_unique
from app.core.utils.common_utils import jprint, rich_print
from app.core.utils.pydantic_utils import inst_dict, list_dict
from app.support import Drink, DrinkService, Subcategory, TranslateRawData
from app.support.drink.repository import DrinkRepository
# from app.core.utils.common_utils import jprint
from app.support.ollama.model import ISOLanguage, Prompt, Proption, WriterRule
from app.support.ollama.repository import ISOLanguageRepository, PromptRepository, ProptionRepository, \
    WriterRuleRepository
from app.support.subcategory.repository import SubcategoryRepository
from app.support.vllm.dataclasses import DrinkTranslateData, HandbookTranslateData
from app.support.vllm.model import TmpTranslate, TranslateHelper
from app.support.vllm.repository import TmpTranslateRepository, TranslateRawDataRepository


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

    @background_unique
    async def handbook_translate(self, session_factory, translation_service: TranslationService,
                                 dataclass: HandbookTranslateData):
        """
            перевод справочников
            0. язык двух символьный код
            1. получаем prompts
            2. определяем поля для источника и поля для перевода
            3. отфильтровываем и получаем (id, value in name_{lang}) where name_{dest} is null
            4. отправляем на перевод
            5. получаеv -> передаем на сохранение (update)
        """
        tmp_model = TmpTranslate
        tmp_repo = TmpTranslateRepository
        last_id = 0
        errors = []  # список ошибок [[word, bad_trans, good_trans]]
        while True:  # бесконечый цикл пока есть записи handbooks
            # 3. get data
            async with session_factory() as session:
                phrases, last_id = await self.fetch_data_chunk(session, dataclass, last_id)
                await session.commit()
            # 4.0 translate
            result = await translation_service.real_batch(phrases, dataclass)
            # 4.1 evaluate
            evaluated: List[dict] = await translation_service.evaluate_translations_batch(result)
            # 4.2. extend error list
            # evaluated.get('errors') = [['Moutere', 'Моттера (Moutere)', 'Моттера']]
            err = [errors for item in evaluated if (errors := item.get('errors'))]
            errors.extend(err)
            logger.success(f'оценено {len(evaluated)} записей. Результаты оценки ниже.')
            # 5. save to temporary file
            # 5.0. prepaire for save (score added)
            distill = self.__tmp_data_validate__(result, evaluated, dataclass)

            # 5.1. save to tmp_model
            async with session_factory() as session:
                response: int = await tmp_repo.bulk_create_no_return(distill, tmp_model, session)
                await session.commit()
            logger.success(f'{response} записей добавлено во временную таблицу')
            # 5.2. оценка качества перевода
            quality = self.__score_analyse__(distill, dataclass.score_threshold, errors)
            if not quality or not last_id:
                break
        # 6.0 implementation to real database
        # 6.1. выдать сводку - сколько записей больше или равно threshold и меньше по таблицам
        async with session_factory() as session:
            await self.__stats__(session, dataclass.score_threshold)
            # 6.5. заполнение TranslateHelper
            await self.__add_translatehelper__(errors)
            await session.commit()
            session.expire_all()
        return None

    async def fetch_data_chunk(self, session: AsyncSession, d: HandbookTranslateData, last_id: int) -> tuple:
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
        sql = raw_sql.format(origin=d.source_field, dest=d.target_field, handbook=d.handbook, last_id=last_id,
                             chunk=d.chunk)
        stmt = text(sql)
        # compiled_pg = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        # print(compiled_pg)
        response = await session.execute(stmt)
        rows = response.all()
        result = tuple((row.id, row._mapping[d.source_field]) for row in rows)
        logger.success(f'получено {len(result)} записей для перевода')
        if len(result) < d.chunk:
            last_id = None
        else:
            last_id = result[-1][0]
        return result, last_id

    def __tmp_data_validate__(self, data: dict, evaluated: List[dict],
                              d: HandbookTranslateData) -> List[dict]:
        """
            преобразование и валидация данных для добавления во временную таблицу
            return:
            guid: int   id записи
            table: str  имя таблицы
            field: str  имя поля
            lang: str
            origin: str оригинал
            translate: str перевод
            score: int
        """
        evo = {d.get('drink_id'): int(d.get('total_score')) for d in evaluated}
        distill = [{'guid': v.get('drink_id'),
                    'table': d.handbook,
                    'field': d.target_field,
                    'lang': d.language_destination,
                    'origin': v.get('origin'),
                    'translate': v.get('result'),
                    'score': evo.get(v.get('drink_id'))} for v in data]
        return distill

    def __score_analyse__(self, distill: List[dict], threshold: int, errors: list):
        """
            анализ оценок качества переводов
            если >50% ниже score_threshold
            возвращает false и цикл прерывается
        """
        items = [item.get('score') for item in distill]
        less = sum(x < threshold for x in items) / len(items) * 100
        if less < 50:
            return True
        logger.warning(
                f'Качество перевода менее 50%. Останавливаем перевод. В ходе перевода выявлено '
                f'{len(errors)} слов и выражений. Сейчас они будут добавлены в словарь трудностей и можно запустить '
                f'перевод заново - качество доджно улучшиться'
        )
        return False

    async def __stats__(self, session: AsyncSession, threshold: int) -> List[dict]:
        """
            сводка по качеству перевода
            # удаление не качественного контента
            # добавление качественного контента по таблицам
            # очистка результата
        """
        Tmp = get_model_by_tablename('tmptranslates')
        # 1. Статистика
        result = await session.execute(
            select(Tmp.table, Tmp.field, func.count().filter(Tmp.score >= threshold).label('good'),
                   func.count().filter(Tmp.score < threshold).label('bad')
                   ).group_by(Tmp.table, Tmp.field)
        )
        stats = [{key: str(value) for key, value in row._mapping.items()} for row in result]
        rich_print(stats, 'статистика перевода')

        # 6.2. удалить плохие переводы
        await self.__del_bad_scores__(stats, session)
        # 6.3. обновить таблицы переводами
        result = await self.__update_handbook__(stats, session)
        # 6.4. очистка таблицы
        await self.__clear_tmptable__(session)

        return stats

    async def __del_bad_scores__(self, stats: List[Dict], session: AsyncSession):
        """ удаление
            плохих отметок
        """
        model = TmpTranslate
        repository = TmpTranslateRepository
        result = await repository.bulk_delete(session, model, model.score < 10)
        logger.info(f'deleted {result} records with bad score')
        return None

    async def __update_handbook__(self, stats, session):
        result: list = []
        for row in stats:
            table_name = row.get('table')
            field_name = row.get('field')
            model = get_model_by_tablename(table_name)
            target_column = getattr(model, field_name)
            stmt = (update(model)
                    .where(model.id == TmpTranslate.guid)
                    .where(TmpTranslate.table == table_name)
                    .where(TmpTranslate.score == 10)
                    .values({target_column: TmpTranslate.translate}))
            # compiled_pg = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
            # print(compiled_pg)
            response = await session.execute(stmt)
            result.append({'table': model.__name__, 'field': field_name, 'updated records': f'{response.rowcount}'})
            # result.append({'table': model.__name__, 'field': field_name, 'updated records': f'{row.get('good')}'})
        rich_print(result, 'количество обновленных записей')
        # session.execute(text(f"TRUNCATE TABLE {Country.__tablename__} RESTART IDENTITY CASCADE;"))
        # session.commit()
        return result

    async def __clear_tmptable__(self, session: AsyncSession):
        """
        очистка временной таблицы
        """
        await session.execute(text(f"TRUNCATE TABLE {TmpTranslate.__tablename__} RESTART IDENTITY CASCADE;"))

    async def __add_translatehelper__(self, errors: List) -> int:
        """
        добавление ошибок в TranslateHelper
        """
        # 0. convert [(word, wrong, drow)] => [{'word': word, drow: [drow]}]
        jprint(errors)
        logger.critical('errors')
        result = defaultdict(list)
        for key, _, val in errors:
            result[key].append(val)
        data: List[dict] = [{'word': key, 'drow': val} for key, val in result.items()]
        logger.critical('__add_transferhelper__')
        jprint(data)

    @background_unique
    async def drink_translate(
            self, session_factory, translation_service: TranslationService,
            data: DrinkTranslateData
            # system_prompt: str,
            # language_origin: str, language_destination: str, user_prompt: str, params: str, chunk: int,
            # field_name: str = 'description'
    ):
        """
        0. исходные данные: data: DrinkTranslateData
        1. Запуск цикла: первый tier - если средний балл низкий - прерывается
        """
        for subcat_id, drink in data.subcategories.items():
            last_id = 0
            while True:
                async with session_factory() as session:
                    datas, last_id = await self.__fetch_drink_chunk__(session, data.source_field,
                                                                      data.target_field, subcat_id,
                                                                      data.chunk, last_id
                                                                      )
                    await session.commit()
                # 4. translate
                result = await translation_service.real_batch(
                    datas, data.system_prompt, data.user_prompt, data.params, data.language_destination, drink  # subj
                )
                jprint(result)
                last_id = None
                if not last_id:
                    break
            break
        return

        tmp_model = TmpTranslate
        tmp_repo = TmpTranslateRepository
        last_id = 0
        return None

    async def __fetch_drink_chunk__(self, session: AsyncSession, source_field: str, target_field: str,
                                    subcat_id: int, chunk: int, last_id: int = 0) -> tuple:
        """
        получение данных перевода
        """
        raw_sql = """
        SELECT id, {source_field} FROM drinks
        WHERE COALESCE({target_field},'') = '' AND COALESCE({source_field}, '') != ''
        AND subcategory_id = {subcat_id}
        AND id > {last_id}
        ORDER BY id
        LIMIT {chunk};
        """
        sql = raw_sql.format(source_field=source_field, target_field=target_field,
                             subcat_id=subcat_id, last_id=last_id, chunk=chunk)
        stmt = text(sql)
        # compiled_pg = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        response = await session.execute(stmt)
        rows = response.all()
        result = tuple((row.id, row._mapping[source_field]) for row in rows)
        logger.success(f'получено {len(result)} записей для перевода')
        if len(result) < chunk:
            last_id = None
        else:
            last_id = result[-1][0]
        return result, last_id


class TranslateRawDataService(Service):
    default = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']


class TmpTranslateService(Service):
    default = ['id', 'table', 'field']


class DrinkTranslateScoreService(Service):
    default = ['id']


class TranslateHelperService(ArrayService, Service):
    default = ['id', 'word']
