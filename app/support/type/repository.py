# app/support/type/repository.py

from app.support.type.model import Type
from app.core.repositories.sqlalchemy_repository import Repository


class TypeRepository(Repository):
    model = Type
