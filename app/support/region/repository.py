# app/support/region/repository.py

from app.support.region.model import Region
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class RegionRepository(Repository):
    model = Region

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Region).options(selectinload(Region.country))
