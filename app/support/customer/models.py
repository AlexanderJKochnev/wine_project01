# app/support/customer/models.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship, Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401


class Customer(Base):
    fisrtname: Mapped[str_null_true]
    lastname: Mapped[str_null_true]
    account: Mapped[str_null_index]

    wartehouses: Mapped[List["Warehouse"]] = relationship("Warehouse",  # noqa F821
                                                          back_populates="category",
                                                          cascade="all, delete-orphan")
