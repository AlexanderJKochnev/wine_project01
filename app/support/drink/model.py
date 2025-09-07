# app/support/drink/model.py
from __future__ import annotations

from typing import List, TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, Integer, String, Text, text  # noqa: F401
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.base_model import (Base, BaseAt, BaseDescription,
                                        boolnone, ion, str_null_true, str_uniq, volume)
from app.core.config.project_config import settings
from app.core.utils.common_utils import plural


if TYPE_CHECKING:
    from app.support.sweetness.model import Sweetness
    from app.support.color.model import Color
    from app.support.category.model import Category
    from app.support.item.model import Item
    from app.support.subregion.model import Subregion


class Drink(Base, BaseDescription, BaseAt):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'drink'
    plural_name = plural(single_name)
    # наименование на языке производителя
    title_native: Mapped[str_null_true]
    subtitle_native: Mapped[str_null_true]
    # наименование на международном (англ) языке
    title: Mapped[str_uniq]
    subtitle: Mapped[str_null_true]

    alc: Mapped[volume]
    sugar: Mapped[volume]
    aging: Mapped[ion]
    sparkling: Mapped[boolnone]
    # Foreign Keys on-to-many
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    subregion_id: Mapped[int] = mapped_column(ForeignKey("subregions.id"), nullable=False)
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id"), nullable=True)
    sweetness_id: Mapped[int] = mapped_column(ForeignKey("sweetness.id"), nullable=True)

    # Relationships fields (
    category: Mapped["Category"] = relationship(back_populates="drinks")
    subregion: Mapped["Subregion"] = relationship(back_populates="drinks")
    color: Mapped["Color"] = relationship(back_populates="drinks")
    sweetness: Mapped["Sweetness"] = relationship(back_populates="drinks")

    # обратная связь
    items = relationship("Item", back_populates=single_name,
                         cascade=cascade,
                         lazy=lazy)

    # Связь через промежуточную модель
    # food_associations = relationship("DrinkFood", back_populates="drink", cascade="all, delete-orphan")
    # foods = relationship("Food", secondary="drink_food_associations", viewonly=True, lazy="selectin")

    # Прямые связи с промежуточной таблицей
    food_associations = relationship("DrinkFood",
                                     back_populates="drink",
                                     cascade="all, delete-orphan",
                                     overlaps="foods")
    foods = relationship("Food",
                         secondary="drink_food_associations",
                         back_populates="drinks",
                         lazy="selectin",
                         viewonly=False,  # чтобы можно было использовать в form
                         overlaps="food_associations,drink")
    # Важно: viewonly=False — позволяет SQLAlchemy корректно обновлять связь через .foods

    """ ALTERNATIVE VERSION
    @property
    def foods(self):
        return [association.food for association in self.food_associations]
    """

    def __str__(self):
        return f"{self.title} - {self.title_native})"


class DrinkFood(Base):
    __tablename__ = "drink_food_associations"

    drink_id = Column(Integer, ForeignKey("drinks.id"), primary_key=True)
    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)

    # Пример дополнительного поля (можно расширять)
    priority = Column(Integer, default=0)

    # Relationships
    drink = relationship("Drink", back_populates="food_associations", overlaps='foods')
    food = relationship("Food", back_populates="drink_associations", overlaps='drinks,foods')

    def __str__(self):
        return f"Drink {self.drink_id} - Food {self.food_id} (Priority: {self.priority})"
