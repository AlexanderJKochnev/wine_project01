# app/support/food/model.py
from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.core.config.project_config import settings
from app.core.models.base_model import BaseFull
from app.core.utils.common_utils import plural

if TYPE_CHECKING:
    from app.support.drink.model import DrinkFood
    from app.support.superfood.model import Superfood


class Food(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'food'
    plural_name = plural(single_name)

    superfood_id: Mapped[int] = mapped_column(ForeignKey("superfoods.id"), nullable=True)
    superfood: Mapped["Superfood"] = relationship(back_populates=plural_name, lazy=lazy)

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
