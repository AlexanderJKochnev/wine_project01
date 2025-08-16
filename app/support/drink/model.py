# app/support/drink/model.py
from __future__ import annotations
from sqlalchemy import String, Text, text, ForeignKey, Integer, Column   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)
from typing import List, TYPE_CHECKING
from app.core.models.image_mixin import ImageMixin
from app.core.models.base_model import (Base, BaseLang, BaseEn, BaseAt,
                                        str_null_true, volume, ion, boolnone)

if TYPE_CHECKING:
    from app.support.sweetness.model import Sweetness
    from app.support.color.model import Color
    from app.support.food.model import Food
    from app.support.region.model import Region
    from app.support.category.model import Category


class Drink(Base, BaseLang, BaseEn, BaseAt, ImageMixin):
    subtitle: Mapped[str_null_true]
    alcohol: Mapped[volume]
    sugar: Mapped[volume]
    aging: Mapped[ion]
    sparkling: Mapped[boolnone]
    """category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="drinks", lazy="joinload", join_depth=1)  # noqa F821

    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"), nullable=True)
    food: Mapped["Food"] = relationship(back_populates = "drinks", lazy="joinload", join_depth=1)  # noqa F821

   """

    items: Mapped[List["Item"]] = relationship("Item",  # noqa F821
                                               back_populates="drink",
                                               cascade="all, delete-orphan")
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False)
    region: Mapped["Region"] = relationship(back_populates="drinks")
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    category: Mapped["Category"] = relationship(back_populates="drinks")
    food_id: Mapped[int] = mapped_column(ForeignKey("foods.id"), nullable=True)
    food: Mapped["Food"] = relationship(back_populates="drinks")
    color_id: Mapped[int] = mapped_column(ForeignKey("colors.id"), nullable=True)
    color: Mapped["Color"] = relationship(back_populates="drinks")
    sweetness_id: Mapped[int] = mapped_column(ForeignKey("sweetness.id"), nullable=True)
    sweetness: Mapped["Sweetness"] = relationship(back_populates="drinks")
