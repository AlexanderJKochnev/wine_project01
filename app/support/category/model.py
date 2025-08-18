# app/support/category/model.py
from __future__ import annotations
from sqlalchemy.orm import relationship
from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt


class Category(Base, BaseEn, BaseLang, BaseAt):
    # count_drink: Mapped[nmbr] = mapped_column(server_default=text('0'))
    # Обратная связь: один ко многим
    drinks = relationship("Drink", back_populates="category", lazy="select")
