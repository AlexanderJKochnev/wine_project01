# app/support/drink/repository.py
from app.support.drink.models import Drink
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# DrinkRepository = RepositoryFactory.get_repository(Drink)
class DrinkRepository(Repository):
    model = Drink

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Drink).options(selectinload(Drink.category),
                                     selectinload(Drink.food),
                                     selectinload(Drink.sweetness),
                                     selectinload(Drink.color))
