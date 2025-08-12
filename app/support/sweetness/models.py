# app/support/sweetness/models.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,              # noqa: F401
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401
from typing import List


class Sweetness(Base):
    # Обратная связь: один ко многим
    drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="sweetness",
                                                 cascade="all, delete-orphan")
