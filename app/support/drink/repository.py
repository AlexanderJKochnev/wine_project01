# app/support/drink/repository.py
from app.support.drink.models import Drink
from app.core.repositories.sqlalchemy_repo2 import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.core.config.database.db_noclass import get_db


# DrinkRepository = RepositoryFactory.get_repository(Drink)
class DrinkRepository(Repository):
    model = Drink

    def get_query(self):
        # Добавляем загрузку связи с Category
        return select(Drink).options(selectinload(Drink.category))
