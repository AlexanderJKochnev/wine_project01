# app/support/drink/models.py

from __future__ import annotations
from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
#     from app.support.category.models import Category


class Drink(Base):
    subtitle: Mapped[str_null_true]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False)
    # Добавляем relationship
    category: Mapped["Category"] = relationship(back_populates="drinks")  # noqa F821
