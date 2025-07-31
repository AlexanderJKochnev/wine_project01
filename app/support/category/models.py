# app/support/category/models.py

from sqlalchemy import String, Text, text   # noqa: F401
from sqlalchemy.orm import (relationship,   # noqa: F401
                            Mapped, mapped_column)    # noqa: F401
from sqlalchemy import ForeignKey   # noqa: F401
from app.core.models.base_model import (Base, int_pk, nmbr,
                                        str_uniq, str_null_true)


class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int_pk]
    name: Mapped[str_uniq]
    description: Mapped[str_null_true]
    count_drink: Mapped[nmbr] = mapped_column(server_default=text('0'))
    # Обратная связь: один ко многим
    drinks = relationship("Drink",
                          back_populates="category",
                          cascade="all, delete-orphan")

    def __str__(self):
        return self.name
        # return (f"{self.__class__.__name__}("
        #        f"id={self.id}, category_name={self.name!r})")

    def __repr__(self):
        # return f"<Category(name={self.name})>"
        return str(self)
