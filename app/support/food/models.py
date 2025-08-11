# app/support/food/models.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401
from sqlalchemy.orm import relationship, Mapped
from typing import List


class Food(Base):
    drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="food", cascade="all, delete-orphan")
