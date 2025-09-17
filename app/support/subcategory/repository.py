# app/support/subcategory/repository.py

from app.support.subcategory.model import Subcategory
from app.core.repositories.sqlalchemy_repository import Repository


class SubcategoryRepository(Repository):
    model = Subcategory
