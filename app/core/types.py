# app.core.types.py
from typing import Type, TypeVar
from sqlalchemy.orm import DeclarativeBase
# from app.core.models.base_model import Base


class Base(DeclarativeBase):
    pass


# ModelType = TypeVar("ModelType", bound=Base)
ModelType = TypeVar("ModelType", bound=Base)