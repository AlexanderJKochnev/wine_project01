# app/support/food/model.py
from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from app.core.models.base_model import BaseFull

if TYPE_CHECKING:
    from app.support.drink.model import DrinkFood


class Food(BaseFull):

    # Связь с промежуточной таблицей
    drink_associations: Mapped[List["DrinkFood"]] = relationship("DrinkFood",
                                                                 back_populates="food",
                                                                 cascade="all, delete-orphan",
                                                                 overlaps="drinks,foods")
    drinks = relationship("Drink", secondary="drink_food_associations", back_populates="foods",
                          lazy="selectin", overlaps="drink_associations,food,drink,food_associations")

    """ alternative version
    @property
    def drinks(self):
        return [association.drink for association in self.drink_associations]
    """
