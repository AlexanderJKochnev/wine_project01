# app/support/sweetness/repository.py

from app.support.sweetness.model import Sweetness
from app.core.repositories.sqlalchemy_repository import Repository
# from sqlalchemy.orm import selectinload
# from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# SweetnessRepository = RepositoryFactory.get_repository(Sweetness)
class SweetnessRepository(Repository):
    model = Sweetness
