# app/support/subregion/repository.py

from app.support.subregion.model import Subregion
from app.support.region.model import Region
from app.core.repositories.sqlalchemy_repository import Repository, ModelType
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class SubregionRepository(Repository):
    model = Subregion

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(Subregion).options(selectinload(Subregion.region),
                                         selectinload(Region.country))
