# app/support/drink/model.py
from __future__ import annotations
from sqlalchemy import String, Text, text, ForeignKey, Integer, Column   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)
from typing import List, TYPE_CHECKING
# from app.core.models.image_mixin import ImageMixin
from app.core.models.base_model import (Base, BaseLang, BaseEn, BaseAt,
                                        str_null_true, volume, ion, boolnone)
from sqlalchemy.orm import (DeclarativeBase, Mapped,
                            declared_attr, mapped_column)

if TYPE_CHECKING:
    from app.support.sweetness.model import Sweetness
    from app.support.color.model import Color
    from app.support.food.model import Food
    from app.support.region.model import Region
    from app.support.category.model import Category
    from app.support.item.model import Item


class Drink(Base, BaseLang, BaseEn, BaseAt):
    subtitle: Mapped[str_null_true]
    alcohol: Mapped[volume]
    sugar: Mapped[volume]
    aging: Mapped[ion]
    sparkling: Mapped[boolnone]
    # Foreign Keys on-to-many
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    # food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"), nullable=True)
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id"), nullable=True)
    sweetness_id: Mapped[int] = mapped_column(ForeignKey("sweetness.id"), nullable=True)

    # Relationships fierlds
    items: Mapped[List["Item"]] = relationship("Item", back_populates="drink",
                                               cascade="all, delete-orphan",
                                               lazy="selectin")
    region: Mapped["Region"] = relationship(back_populates="drinks", lazy="selectin")
    category: Mapped["Category"] = relationship(back_populates="drinks", lazy="selectin")
    # food: Mapped["Food"] = relationship(back_populates="drinks")
    color: Mapped["Color"] = relationship(back_populates="drinks", lazy="selectin")
    sweetness: Mapped["Sweetness"] = relationship(back_populates="drinks", lazy="selectin")

    # Связь через промежуточную модель
    food_associations = relationship("DrinkFood", back_populates="drink", cascade="all, delete-orphan")
    foods = relationship("Food", secondary="drink_food_associations", viewonly=True, lazy="selectin")


class DrinkFood(Base):
    # __tablename__ = "drink_food_associations"

    drink_id = Column(Integer, ForeignKey("drinks.id"), primary_key=True)
    food_id = Column(Integer, ForeignKey("foods.id"), primary_key=True)

    # Пример дополнительного поля (можно расширять)
    priority = Column(Integer, default=0)

    # Relationships
    drink = relationship("Drink", back_populates="food_associations")
    food = relationship("Food", back_populates="drink_associations")


    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "drink_food_associations"