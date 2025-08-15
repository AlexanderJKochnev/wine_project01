# app/support/drink/repository.py
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.core.repositories.sqlalchemy_repository import Repository
from app.support.drink.model import Drink
from app.support.region.model import Region


# DrinkRepository = RepositoryFactory.get_repository(Drink)
class DrinkRepository(Repository):
    model = Drink

    def get_query(self):
        # Добавляем загрузку связи с relationships
        """return select(Drink).options(selectinload(Drink.category)
                                     # selectinload(Drink.food),
                                     # selectinload(Drink.sweetness),
                                     # selectinload(Drink.color)
                                     )"""
        return select(Drink).options(joinedload(Drink.region)
                                     .joinedload(Region.country),
                                     joinedload(Drink.category),
                                     joinedload(Drink.food),
                                     joinedload(Drink.color),
                                     joinedload(Drink.sweetness),
                                     )
