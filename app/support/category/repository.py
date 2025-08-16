# app/support/category/repository.py

from app.support.category.model import Category
from app.core.repositories.sqlalchemy_repository import Repository


# CategoryRepository = RepositoryFactory.get_repository(Category)
# class CategoryRepository(Repository):
#    model = Category

class CategoryRepository(Repository):
    model = Category
