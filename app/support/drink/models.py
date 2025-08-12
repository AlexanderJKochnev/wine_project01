# app/support/drink/models.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)
from typing import List
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401


class Drink(Base):
    subtitle: Mapped[str_null_true]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="drinks")  # noqa F821

    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"), nullable=True)
    food: Mapped["Food"] = relationship(back_populates = "drinks")  # noqa F821

    items: Mapped[List["Item"]] = relationship("Item",  # noqa F821
                                               back_populates="drink",
                                               cascade="all, delete-orphan")
