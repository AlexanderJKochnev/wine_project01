# app/support/customer/model.py
from __future__ import annotations

from sqlalchemy.orm import (Mapped, relationship)

from app.core.models.base_model import (Base, BaseAt, str_null_index, str_null_true, str_uniq)
from app.core.config.project_config import settings
from app.core.utils.common_utils import plural


class Customer(Base, BaseAt):
    login: Mapped[str_uniq]
    firstname: Mapped[str_null_true]
    lastname: Mapped[str_null_true]
    account: Mapped[str_null_index]
    warehouses = relationship("Warehouse", back_populates="customer")
    """warehouses: Mapped[List["Warehouse"]] = relationship("Warehouse",
                                                         back_populates="customer",
                                                         cascade="all, delete-orphan")"""

    def __str__(self):
        return self.login
