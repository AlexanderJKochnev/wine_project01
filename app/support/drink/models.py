# app/support/drink/models.py
""" SQLAlchemy models """
from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import (Base, int_pk,
                                        str_uniq, str_null_true)
# from datetime import date
# from app.support.major.models import Major


class Drink(Base):
    id: Mapped[int_pk]
    title: Mapped[str_uniq]
    subtitle: Mapped[str]
    description: Mapped[str_null_true]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False)
    # Добавляем relationship
    category: Mapped["Category"] = (        # NOQA F821
            relationship(back_populates="drinks"))

    def __str__(self):
        return self.title
        # return (f"{self.__class__.__name__}(id={self.id}, "
        #         f"title={self.title!r},"
        #         f"subtitle={self.subtitle!r})")

    def __repr__(self):
        return self.title

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subtitle": self.subtitle,
            "description": self.description,
            "category_id": self.category_id
        }
