# app/support/customer/model.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship, Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import (Base, BaseAt, str_uniq,
                                        str_null_true, str_null_index)
from typing import List


"""  переделать - убрать многоязыковую поддержку """


class Customer(Base, BaseAt):
    login: Mapped[str_uniq]
    fisrtname: Mapped[str_null_true]
    lastname: Mapped[str_null_true]
    account: Mapped[str_null_index]

    warehouses: Mapped[List["Warehouse"]] = relationship("Warehouse",  # noqa F821
                                                         back_populates="customer",
                                                         cascade="all, delete-orphan")
