# app.support.vllm.repository.py
from typing import Any, Dict, List, Union
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import Repository
from app.core.types import ModelType
from app.core.utils.ahocorasick import get_loaded_extractor_tasks, refresh_extractor
from app.support import Drink
from app.support.vllm.model import DrinkTranslateScore, TmpTranslate, TranslateHelper, TranslateRawData


class VllmRepository:
    pass


class TranslateRawDataRepository(Repository):
    model = TranslateRawData

    @classmethod
    def get_selectin(cls):
        return (selectinload(TranslateRawData.drink).selectinload(Drink.subcategory),
                selectinload(TranslateRawData.prompt),
                selectinload(TranslateRawData.writerrule),
                selectinload(TranslateRawData.proption))

    @classmethod
    def get_query(cls, model: ModelType):
        """ Добавляем загрузку связи с relationships
            Обратить внимание! для последовательной загрузки использовать точку.
            параллельно запятая
        """
        return select(TranslateRawData).options(*cls.get_selectin())


class TmpTranslateRepository(Repository):
    model = TmpTranslate


class DrinkTranslateScoreRepository(Repository):
    model = DrinkTranslateScore


class TranslateHelperRepository(Repository):
    model = TranslateHelper

    @classmethod
    async def refresh_corasick(cls, session: AsyncSession):
        """
        обновление боров ахо карасика
        'translator_{lang_origin}_{lang_destin}'
        """
        # активные боры 'translator_{lang_origin}_{lang_destin}', 'cleaner'
        boras: list = get_loaded_extractor_tasks()
        for key in boras:
            if key == 'cleaner':
                db_filter = {'shit': True}
            else:
                s = key.split('_')
                db_filter = {'shit': False, 'origin': s[-2], 'destin': s[-1]}
            logger.warning(f'{key=}, {db_filter}=')
            await refresh_extractor(task_type=key, session=session, db_filter=db_filter)
        # await refresh_extractor(task_type='cleaner', session=session, db_filter={'shit': True})
        # await refresh_extractor(task_type='translator', session=session, db_filter={'shit': False})

    @classmethod
    async def create(cls, obj: ModelType, model: ModelType, session: AsyncSession) -> ModelType:
        result = await super().create(obj, model, session)
        await cls.refresh_corasick(session)
        return result

    @classmethod
    async def patch(cls, obj: ModelType,
                    data: Dict[str, Any], session: AsyncSession) -> Union[ModelType, dict, None]:
        result = await super().patch(obj, data, session)
        await cls.refresh_corasick(session)
        return result

    @classmethod
    async def delete(cls, obj: ModelType, session: AsyncSession) -> bool:
        result = await super().delete(obj, session)
        await cls.refresh_corasick(session)
        return result

    @classmethod
    async def bulk_create_no_return(
        cls, data: List[Dict], model: ModelType, session: AsyncSession
    ) -> int:
        result = await super().bulk_create_no_return(data, model, session)
        await cls.refresh_corasick(session)
        return result

    @classmethod
    async def search_all(cls, search: str,
                         model: ModelType,
                         session: AsyncSession, limit: int = 20) -> List:
        stmt = select(model).where(model.word.contains(search))
        """
        stmt = select(User).where(
                or_(
                        User.name.ilike(f"%{search_term}%"),
                        func.array_to_string(User.tags, ',').ilike(f"%{search_term}%")
                        )
                )
        """
        return await cls.nonpagination(stmt, session)
