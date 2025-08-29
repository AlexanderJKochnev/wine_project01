# app/support/drink/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import Repository
from app.support.drink.model import Drink
from app.support.region.model import Region


# from app.core.utils.image_utils import ImageService


# DrinkRepository = RepositoryFactory.get_repository(Drink)
class DrinkRepository(Repository):
    model = Drink

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Drink).options(selectinload(Drink.region).
                                     selectinload(Region.country),
                                     selectinload(Drink.category),
                                     # joinedload(Drink.food),
                                     selectinload(Drink.color),
                                     selectinload(Drink.sweetness),
                                     selectinload(Drink.foods))
        """
        return select(Drink).options(joinedload(Drink.region)
                                     .joinedload(Region.country),
                                     joinedload(Drink.category),
                                     # joinedload(Drink.food),
                                     joinedload(Drink.color),
                                     joinedload(Drink.sweetness),
                                     )
        """
