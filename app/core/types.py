# app.core.types.py
from typing import Type, TypeVar

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.mutable import MutableList, MutableSet
from sqlalchemy.orm import DeclarativeBase
# from app.core.models.base_model import Base


class Base(DeclarativeBase):
    pass


# ModelType = TypeVar("ModelType", bound=Base)
ModelType = TypeVar("ModelType", bound=Base)

# Применяем MutableSet.as_mutable к типу ARRAY
""" после этого с ними можно работать как с обычными списками сетами append, extend, remove """
SetArrayType = MutableSet.as_mutable(ARRAY(String))
ListArrayType = MutableList.as_mutable(ARRAY(String))