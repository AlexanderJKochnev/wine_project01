# app/support/drink/repository.py
from app.core.repositories.repo_factory import RepositoryFactory
from app.support.drink.models import Drink


DrinkRepository = RepositoryFactory.get_repository(Drink)
