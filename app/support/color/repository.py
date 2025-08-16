# app/support/color/repository.py

from app.support.color.model import Color
from app.core.repositories.sqlalchemy_repository import Repository
# from sqlalchemy.orm import selectinload
# from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# ColorRepository = RepositoryFactory.get_repository(Color)
class ColorRepository(Repository):
    model = Color
