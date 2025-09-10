# app/support/drink/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import Repository, ModelType
from app.support.drink.model import Drink, DrinkFood
from app.support.subregion.model import Subregion
from app.support.region.model import Region


class DrinkRepository(Repository):
    model = Drink

    def get_query(self, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(Drink).options(selectinload(Drink.subregion).
                                     selectinload(Subregion.region),
                                     selectinload(Region.country),
                                     selectinload(Drink.category),
                                     selectinload(Drink.color),
                                     selectinload(Drink.sweetness),
                                     selectinload(Drink.foods),
                                     selectinload(Drink.food_associations).joinedload(DrinkFood.food))
