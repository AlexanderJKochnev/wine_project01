# app/support/region/repository.py

from app.support.region.model import Region
from app.core.repositories.sqlalchemy_repository import Repository, ModelType
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class RegionRepository(Repository):
    model = Region

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(Region).options(selectinload(Region.country))
