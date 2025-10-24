# app/support/subcategory/repository.py

from app.core.repositories.sqlalchemy_repository import Repository
from app.support.subcategory.model import Subcategory


class SubcategoryRepository(Repository):
    model = Subcategory
