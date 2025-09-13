# app/support/Item/repository.py

from app.support.item.model import Item
from app.core.repositories.sqlalchemy_repository import Repository, ModelType
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.support.drink.model import Drink
from app.support.warehouse.model import Warehouse
from app.support.subregion.model import Subregion
from app.support.region.model import Region
from app.support.country.model import Country
from app.support.category.model import Category
from app.support.color.model import Color
from app.support.sweetness.model import Sweetness
from app.support.food.model import Food, DrinkFood

# from app.core.config.database.db_noclass import get_db


# ItemRepository = RepositoryFactory.get_repository(Item)
class ItemRepository(Repository):
    model = Item

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(Item).options(selectinload(Item.drink).selectinload(Drink.category),
                                    selectinload(Item.warehouse))
