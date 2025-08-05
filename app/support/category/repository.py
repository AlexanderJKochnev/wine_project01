# app/support/category/repository.py

from app.core.repositories.repo_factory import RepositoryFactory
from app.support.category.models import Category

CategoryRepository = RepositoryFactory.get_repository(Category)
