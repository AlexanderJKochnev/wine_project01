# app/support/region/repository.py
"""
    если есть поля с relationships manytoone заполни актуальной информацией процедуру get_query
    для примера см. app/support/drink/repository.py
    ЕСЛИ ТАКИХ ПОЛЕЙ НЕТ - УДАЛИ ЭТУ ПРОЦЕДУРУ ПОЛНОСТЬЮ
"""

from app.support.region.models import Region
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# RegionRepository = RepositoryFactory.get_repository(Region)
class RegionRepository(Repository):
    model = Region

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Region).options(selectinload(Region.country))
