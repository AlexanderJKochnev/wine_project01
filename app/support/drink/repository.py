# app/support/drink/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import Repository, ModelType
from app.support.drink.model import Drink, DrinkFood, DrinkVarietal
from app.support.subregion.model import Subregion
from app.support.region.model import Region


class DrinkRepository(Repository):
    model = Drink

    @classmethod
    def get_query(csl, model: ModelType):
        """ Добавляем загрузку связи с relationships
            Обратить внимание! для последовательной загрузки использовать точку.
            параллельно запятая
        """
        return select(Drink).options(selectinload(Drink.subregion).
                                     selectinload(Subregion.region).
                                     selectinload(Region.country),
                                     selectinload(Drink.category),
                                     selectinload(Drink.color),
                                     selectinload(Drink.sweetness),
                                     selectinload(Drink.foods),
                                     selectinload(Drink.food_associations).joinedload(DrinkFood.food),
                                     selectinload(Drink.varietals),
                                     selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal))
