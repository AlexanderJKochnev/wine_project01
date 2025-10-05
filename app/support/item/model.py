# app/support/Item/model.py

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base_model import Base, BaseAt, ion, money, volume
from app.core.models.image_mixin import ImageMixin

if TYPE_CHECKING:
    from app.support.drink.model import Drink


class Item(Base, BaseAt, ImageMixin):
    vol: Mapped[volume]  # объем тары
    price: Mapped[money]    # цена
    count: Mapped[ion]      # количество

    drink_id: Mapped[int] = mapped_column(ForeignKey("drinks.id"), nullable=False)
    # warehouse_id: Mapped[int] = mapped_column(ForeignKey("warehouses.id"), nullable=True)

    # warehouse: Mapped["Warehouse"] = relationship(back_populates="items")
    drink: Mapped["Drink"] = relationship(back_populates="items")
