# app/support/food/repository.py

from app.support.food.model import Food
from app.core.repositories.sqlalchemy_repository import Repository


# FoodRepository = RepositoryFactory.get_repository(Food)
class FoodRepository(Repository):
    model = Food
