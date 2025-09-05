# app/support/food/model.py
from __future__ import annotations
from sqlalchemy.orm import relationship, Mapped
from typing import List, TYPE_CHECKING
from app.core.models.base_model import Base, BaseAt, BaseEn, BaseLang

if TYPE_CHECKING:
    from app.support.drink.model import DrinkFood


class Food(Base, BaseLang, BaseEn, BaseAt):

    # Связь с промежуточной таблицей
    drink_associations: Mapped[List["DrinkFood"]] = relationship("DrinkFood",
                                                                 back_populates="food",
                                                                 cascade="all, delete-orphan")
    drinks = relationship("Drink", secondary="drink_food_associations", back_populates="foods",
                          lazy="selectin")

    """ alternative version
    @property
    def drinks(self):
        return [association.drink for association in self.drink_associations]
    """
