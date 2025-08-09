# app/support/category/repository.py

from app.support.category.models import Category
from app.core.repositories.sqlalchemy_repo2 import Repository


# CategoryRepository = RepositoryFactory.get_repository(Category)
# class CategoryRepository(Repository):
#    model = Category

class CategoryRepository(Repository):
    model = Category
