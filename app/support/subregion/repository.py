# app/support/subregion/repository.py
from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.utils.alchemy_utils import get_id_field
from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.support.country.model import Country
from app.support.region.model import Region
from app.support.subregion.model import Subregion


class SubregionRepository(Repository):
    model = Subregion

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(Subregion).options(selectinload(Subregion.region).
                                         selectinload(Region.country))
