# app/support/Item/repository.py

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.support.drink.model import Drink, DrinkFood, DrinkVarietal
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.subregion.model import Subregion


# from app.core.config.database.db_noclass import get_db


# ItemRepository = RepositoryFactory.get_repository(Item)
class ItemRepository(Repository):
    model = Item

    @classmethod
    def get_query(cls, model: ModelType):
        return select(model).options(selectinload(Item.drink).options(
            selectinload(Drink.subregion).options(
                selectinload(Subregion.region).options(
                    selectinload(Region.country))),
            selectinload(Drink.category),
            selectinload(Drink.color),
            selectinload(Drink.sweetness),
            selectinload(Drink.foods),
            selectinload(Drink.food_associations).joinedload(DrinkFood.food),
            selectinload(Drink.varietals),
            selectinload(Drink.varietal_associations).joinedload(DrinkVarietal.varietal)),
            selectinload(Item.warehouse)
        )

