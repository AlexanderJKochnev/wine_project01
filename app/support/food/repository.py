# app/support/food/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.support.food.model import Food
from app.support.drink.model import DrinkFood
from app.core.repositories.sqlalchemy_repository import Repository


# FoodRepository = RepositoryFactory.get_repository(Food)
class FoodRepository(Repository):
    model = Food

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(self.model).options(selectinload(Food.drink_associations).joinedload(DrinkFood.drink))