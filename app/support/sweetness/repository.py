# app/support/sweetness/repository.py

from app.support.sweetness.model import Sweetness
from app.core.repositories.sqlalchemy_repository import Repository


class SweetnessRepository(Repository):
    model = Sweetness
