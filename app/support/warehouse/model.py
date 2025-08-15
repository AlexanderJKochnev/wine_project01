# app/support/warehouse/model.py

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from typing import List
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401


class Warehouse(Base):
    address: Mapped[str_null_true]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    # Добавляем relationship
    customer: Mapped["Customer"] = relationship(back_populates="warehouses")  # noqa F821
    items: Mapped[List["Item"]] = relationship("Item",  # noqa F821
                                               back_populates="warehouse", cascade="all, delete-orphan",
                                               )
