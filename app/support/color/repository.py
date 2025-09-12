# app/support/color/repository.py

from app.support.color.model import Color
from app.core.repositories.sqlalchemy_repository import Repository


class ColorRepository(Repository):
    model = Color
