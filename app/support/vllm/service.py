# app.support.vllm.service.py
import time
from collections import defaultdict
from typing import Dict, List, Sequence, Tuple

from fastapi import HTTPException  # , BackgroundTasks,
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy import and_, func, or_, select, text, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.array_service import SetArrayService
from app.core.services.service import Service
from app.core.services.translate_service import TranslationService
from app.core.types import ModelType
from app.core.utils.ahocorasick import clean_text_with_aho, get_translations_with_aho
from app.core.utils.alchemy_utils import get_model_by_tablename
from app.core.utils.backgound_tasks import background_unique
from app.core.utils.common_utils import jprint, rich_print
from app.core.utils.pydantic_utils import list_dict
from app.support import Drink, DrinkService, Subcategory, TranslateRawData
from app.support.drink.repository import DrinkRepository
# from app.core.utils.common_utils import jprint
from app.support.ollama.model import Prompt, Proption, WriterRule
from app.support.ollama.repository import PromptRepository, ProptionRepository, WriterRuleRepository
from app.support.subcategory.repository import SubcategoryRepository
from app.support.vllm.dataclasses import DrinkTranslateData, HandbookTranslateData, LastComposite
from app.support.vllm.model import TmpTranslate, TranslateHelper
from app.support.vllm.repository import TmpTranslateRepository, TranslateHelperRepository, TranslateRawDataRepository

"""
################################################################################################
# __update_handbook__()   это метод который записывает переведенные данные в исходную таблицу  #
################################################################################################
"""


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
                                 dataclass: HandbookTranslateData | DrinkTranslateData):
        """
            перевод справочников и drink
            все данные подготовлены в dataclasses
            запускается бесконечый цикл перевода до тех пока
                а) не переведет все
                б) если количество записей с качеством ниже требуемого меньше 50%
            переведенные тексты анализируются критиком и выдаются ошибки перевода и предложения к их исправению
            предлагаемые изменения записываются в словарь помошника переводчика и используются при следующем/повторном
            переводе.
            но не всегда предложенный перевод удовлетворяет требованиям, поэтому предумотрена процедура ручного
            одобрения перевода. После одобрения перевода - все записи содержащие это словосочетания переводятся заново.
            таким образом качество переводов повышается.
        """
        try:
            tmp_model, tmp_repo, errors = TmpTranslate, TmpTranslateRepository, []
            if isinstance(dataclass, HandbookTranslateData):
                last_id = 0
            else:
                last_id = LastComposite(last_id=0, last_subcategory=0)
            # словари ахо карасики - очистка мусора и подсказки переводчику - зависят от языков исходного и перевода
            cleaner_auto, translator_auto = dataclass.cleaner_auto, dataclass.translator_auto
            while True:  # бесконечый цикл пока есть записи handbooks
                # 3. get data
                final_phrases = await self.__get_phrases__(session_factory, dataclass, last_id, cleaner_auto, translator_auto)
                if len(final_phrases) == 0:
                    logger.critical(f'{len(final_phrases)=} ============')
                    break
                # 4.0 translate / evaluate / error collection / save to tmp_table / quality assurance
                quality, err = await self.__translate_evaluate__(translation_service,
                                                                 final_phrases, dataclass,
                                                                 session_factory, tmp_repo,
                                                                 tmp_model)
                errors.extend(err)
                if not quality or not last_id:
                    logger.critical(f'{quality=} ========{last_id=}====')
                    break
            # обработка и имплементация результатов
            await self.__post_processing__(session_factory, dataclass, errors)
            logger.info('перевод в фонвом режиме закончен')
            return None
        except Exception as e:
            logger.error(e)
            async with session_factory() as session:
                await self.__clear_tmptable__(session)
                await session.commit()
            raise HTTPException(status_code=500, detail=str(e))

    async def __fetch_data_chunk__(self, session: AsyncSession, d: HandbookTranslateData, last_id: int | tuple) -> (
            tuple):
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
        result = tuple((row.id, row._mapping[d.source_field], d.descr) for row in rows)
        logger.success(f'получено {len(result)} записей для перевода')
        if len(result) < d.chunk:
            last_id = None
        else:
            last_id = result[-1][0]
        return result, last_id

    def __tmp_data_validate__(self, data: dict, evaluated: List[dict],
                              d: HandbookTranslateData | DrinkTranslateData) -> List[dict]:
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
        if isinstance(d, HandbookTranslateData):
            table = d.handbook
        else:
            table = 'drinks'
        evo = {d.get('drink_id'): int(d.get('total_score')) for d in evaluated}
        distill = [{'guid': v.get('drink_id'),
                    'table': table,
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
            f'{len(errors)} неточностей. Сейчас они будут добавлены в словарь трудностей и можно '
            f'запустить перевод заново - качество должно улучшиться'
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
        await self.__del_bad_scores__(stats, session, threshold)
        # 6.3. обновить таблицы переводами ВОТ ЭТО ЗАПИСЬ ПЕРЕВОДА В ТАБЛИЦУ ИСТОЧНИК
        result = await self.__update_handbook__(stats, session, threshold)
        # 6.4. очистка таблицы
        await self.__clear_tmptable__(session)

        return stats

    async def __del_bad_scores__(self, stats: List[Dict], session: AsyncSession, threshold: int):
        """ удаление
            плохих отметок
        """
        model = TmpTranslate
        repository = TmpTranslateRepository
        result = await repository.bulk_delete(session, model, model.score < threshold)
        logger.info(f'deleted {result} records with bad score')
        return None

    async def __update_handbook__(self, stats, session, threshold: int):
        """
        обновление исходной таблицы переводом
        """
        result: list = []
        for row in stats:
            table_name = row.get('table')
            field_name = row.get('field')
            model = get_model_by_tablename(table_name)
            target_column = getattr(model, field_name)
            stmt = (update(model)
                    .where(model.id == TmpTranslate.guid)
                    .where(TmpTranslate.table == table_name)
                    .where(TmpTranslate.score == threshold)
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
        result = defaultdict(list)
        for key, *_, val in errors:
            result[key].append(val)
        data: List[dict] = [{'word': key, 'drow': list(set(val))} for key, val in result.items()]
        # СЮДА ВСТАВИТЬ ДОБАВЛЕНИЕ В ТАБЛИЦУ translatehelper
        # logger.critical('__add_transferhelper__ что пойдет в справочник трудных слов')
        rich_print(data, 'справочник трудных слов')

    async def __get_phrases__(self, session_factory, dataclass: HandbookTranslateData | DrinkTranslateData,
                              last_id, cleaner_auto, translator_auto) -> list:
        """
        получение данных для перевода
        """
        if isinstance(dataclass, HandbookTranslateData):
            func = self.__fetch_data_chunk__
        if isinstance(dataclass, DrinkTranslateData):
            func = self.__fetch_drink_chunk__
        async with session_factory() as session:
            # получение фраз
            phrases, last_id = await func(session, dataclass, last_id)
            await session.commit()
            # Шаг 1. Очистка текстов от мусора с помощью первого бора
            # Вход: [(id, text), ...] -> Выход: [(id, revised_text), ...]
            revised_phrases = []
            for phrase_id, txt, descr in phrases:
                revised_text = clean_text_with_aho(txt, cleaner_auto)
                revised_phrases.append((phrase_id, revised_text, descr))
            # Шаг 2. Поиск подсказок перевода по уже очищенному тексту с помощью второго бора
            # Вход: [(id, revised_text), ...] -> Выход: [(id, revised_text, {word: set(str)}), ...]
            final_phrases = []
            for phrase_id, revised_text, descr in revised_phrases:
                translation_hints = get_translations_with_aho(revised_text, translator_auto)
                if translation_hints:
                    print(f'{translation_hints=}')
                final_phrases.append((phrase_id, revised_text, translation_hints, descr))
            return final_phrases

    async def __translate_evaluate__(self, translation_service, final_phrases, dataclass,
                                     session_factory, tmp_repo, tmp_model):
        """
        перевод, оценка, сборка ошибок
        """
        result = await translation_service.real_batch(final_phrases, dataclass)
        # 4.1 evaluate
        evaluated: List[dict] = await translation_service.evaluate_translations_batch(result, dataclass)
        logger.warning('--------evaluated-----------')
        jprint(evaluated)
        logger.warning('--------END evaluated-------')
        # 4.2. extend error list
        # evaluated.get('errors') = [['Moutere', 'Моттера (Moutere)', 'Моттера']]
        err = [errors for item in evaluated if (errors := item.get('errors'))]
        if err:
            err2 = [tuple(item) for sublist in err for item in sublist]
        logger.success(f'оценено {len(evaluated)} записей. Результаты оценки ниже.')
        # 5. save to temporary file
        # 5.0. prepaire for save (score added)
        distill = self.__tmp_data_validate__(result, evaluated, dataclass)
        # if len(distill) == 0:
        #     break
        rich_print(distill, "список записей во временной таблице")
        async with session_factory() as session:
            response: int = await tmp_repo.bulk_create_no_return(distill, tmp_model, session)
            await session.commit()
        logger.success(f'{response} записей добавлено во временную таблицу')
        # 5.2. оценка качества перевода
        quality = self.__score_analyse__(distill, dataclass.score_threshold, errors)
        return quality, err2

    async def __post_processing__(self, session_factory, dataclass, errors):
        """
            обработка результатов
        """
        if len(errors) > 0:
            errors_list_dict = [{'word': e[0], 'wrong': e[1], 'proposed': e[2]} for e in set(errors) if len(e) == 3]
            rich_print(errors_list_dict, 'список ошибок')
        # 6.0 implementation to real database
        # 6.1. выдать сводку - сколько записей больше или равно threshold и меньше по таблицам
        async with session_factory() as session:
            await self.__stats__(session, dataclass.score_threshold)
            # 6.5. заполнение TranslateHelper
            await self.__add_translatehelper__(errors)
            await session.commit()
            session.expire_all()
        return None

    async def __fetch_drink_chunk__(self, session: AsyncSession, d: DrinkTranslateData,
                                    lc: LastComposite | None) -> tuple:
        """
        получение данных перевода
        last_composit = (last_id, last_subcat)
        select(model).options(joinedload(model.category)).where(model.id.in_(subcategory_ids))
        """
        model = Drink
        source_attr = getattr(model, d.source_field)
        target_attr = getattr(model, d.target_field)
        stmt = (select(model.id, source_attr, model.subcategory_id)
                .where(
                and_(or_(target_attr.is_(None), target_attr == ''),
                     and_(source_attr.is_not(None), source_attr != ''),
                     model.subcategory_id.in_(d.subcategory_ids),
                     and_(
                    or_(model.subcategory_id > lc.last_subcategory,
                        and_(model.subcategory_id == lc.last_subcategory, model.id > lc.last_id)))
                     )
                ).order_by(Drink.subcategory_id, Drink.id).limit(d.chunk))

        # compiled_pg = stmt.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})
        # print(compiled_pg)
        response = await session.execute(stmt)
        rows = response.all()
        result = tuple((row.id, row._mapping[d.source_field], row.subcategory_id) for row in rows)
        logger.success(f'получено {len(result)} записей для перевода')
        if len(result) < d.chunk:
            lc = None
        else:
            lc = LastComposite(last_id=result[-1][0], last_subcategory=result[-1][2])
        return result, lc


class TranslateRawDataService(Service):
    default = ['drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id']


class TmpTranslateService(Service):
    default = ['id', 'table', 'field']


class DrinkTranslateScoreService(Service):
    default = ['id']


class TranslateHelperService(SetArrayService, Service):
    default = ['word', 'origin', 'destin']  # по этим полям будет проверяться наличие записей
    repository = TranslateHelperRepository
    model = TranslateHelper
    array_fields = ('drow',)

    @classmethod
    async def get_dict(cls, session: AsyncSession, filter: dict) -> dict:
        stmt = select(cls.model.word, cls.model.drow).filter_by(**filter)
        response = await session.execute(stmt)
        result = dict(response.tuples().all())
        if filter.get('shit'):
            result = {key: next(iter(val)) for key, val in result.items()}
        return result
