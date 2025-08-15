# app/support/Item/model.py


from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt, money, volume


class Item(Base, BaseLang, BaseEn, BaseAt):
    volume: Mapped[volume]
    price: Mapped[money]
    drink_id: Mapped[int] = mapped_column(
        ForeignKey("drinks.id"), nullable=False)
    # Добавляем relationship
    drink: Mapped["Drink"] = relationship(back_populates="items")  # noqa F821

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("warehouses.id"), nullable=True)
    # Добавляем relationship
    warehouse: Mapped["Warehouse"] = relationship(back_populates="items")  # noqa F821