# app/support/Item/repository.py

from app.support.item.models import Item
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# ItemRepository = RepositoryFactory.get_repository(Item)
class ItemRepository(Repository):
    model = Item

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Item).options(selectinload(Item.drink))
