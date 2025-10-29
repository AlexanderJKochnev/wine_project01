# app/support/subcategory/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.support.subcategory.model import Subcategory


class SubcategoryRepository(Repository):
    model = Subcategory

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(Subcategory).options(selectinload(Subcategory.category))
