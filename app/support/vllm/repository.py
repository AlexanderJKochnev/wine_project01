# app.support.vllm.repository.py
from typing import List

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.repositories.array_repository import ArrayRepository
from app.core.repositories.sqlalchemy_repository import MutableSetArrayRepository, Repository
from app.core.types import ModelType
from app.core.utils.common_utils import jprint
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


class TranslateHelperRepository(MutableSetArrayRepository):
    model = TranslateHelper

    @classmethod
    async def bulk_create_or_update(cls, session: AsyncSession, data: List[dict]):
        """
            массовое добавление/обновление
        """
        # 0. получение существующих записей
        filter: dict = data.copy()
        pass

    @classmethod
    async def create(cls, obj: TranslateHelper, model: ModelType, session: AsyncSession) -> ModelType:
        """ создание записи """
        logger.critical(f'--------------0, {obj}')
        tmp = obj.to_dict_fast()
        logger.critical(f'{tmp.get("drow")=}')
        jprint(tmp)
        session.add(TranslateHelper(**tmp))
        logger.critical('--------------1')
        await session.flush()
        await session.refresh(obj)
        logger.critical('--------------2')
        id = obj.id
        await cls.get_related_model_instances(id, model, session)
        logger.critical('--------------3')
        return obj