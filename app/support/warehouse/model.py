# app/support/warehouse/model.py
from __future__ import annotations

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from typing import TYPE_CHECKING
from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt, str_null_true

if TYPE_CHECKING:
    from app.support.customer.model import Customer
    # from app.support.item.model import Item


class Warehouse(Base, BaseLang, BaseEn, BaseAt):
    address: Mapped[str_null_true]
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="warehouses", lazy="selectin")

    items = relationship("Item", back_populates="warehouse", cascade="all, delete-orphan")
    """
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable = False)
    country: Mapped["Country"] = relationship(back_populates = "regions")

    drinks = relationship("Drink", back_populates = "region")
    """
