# app/support/varietal/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.support.varietal.model import Varietal
from app.support.drink.model import DrinkVarietal
from app.core.repositories.sqlalchemy_repository import Repository


# VarietalRepository = RepositoryFactory.get_repository(Varietal)
class VarietalRepository(Repository):
    model = Varietal

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(self.model).options(selectinload(Varietal.drink_associations).joinedload(DrinkVarietal.drink))