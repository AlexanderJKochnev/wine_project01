# app/support/category/models.py

from sqlalchemy import String, Text, text   # noqa: F401
from sqlalchemy.orm import (relationship,   # noqa: F401
                            Mapped, mapped_column)    # noqa: F401
from sqlalchemy import ForeignKey   # noqa: F401
from app.core.models.base_model import Base, nmbr


class Category(Base):
    count_drink: Mapped[nmbr] = mapped_column(server_default=text('0'))
    # Обратная связь: один ко многим
    drinks = relationship("Drink",
                          back_populates="category",
                          cascade="all, delete-orphan")
