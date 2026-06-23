# app.support.vllm.repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import Repository
from app.core.types import ModelType
from app.support import Drink
from app.support.vllm.model import DrinkTranslateScore, TmpTranslate, TranslateRawData


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