# app/support/drink/models.py
""" SQLAlchemy models """
from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true


class Drink(Base):
    subtitle: Mapped[str_null_true]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False)
    # Добавляем relationship
    category: Mapped["Category"] = (        # NOQA F821
            relationship(back_populates="drinks"))

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "category_id": self.category_id
        }
