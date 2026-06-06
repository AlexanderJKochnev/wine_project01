# app/support/tasting/model.py
from __future__ import annotations

# from typing import List, TYPE_CHECKING

# from sqlalchemy.orm import Mapped, relationship
from app.core.config.project_config import settings
from app.core.models.base_model import BaseFull, plural
# from app.service_registry import registers_search_update

# if TYPE_CHECKING:
#     from app.support.drink.model import DrinkTasting


# @registers_search_update("drink_associations.drink.items")
class Tasting(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'tasting'
    plural_name = plural(single_name)
    # Связь с промежуточной таблицей (пока не создана)
    """
    drink_associations: Mapped[List["DrinkTasting"]] = relationship("DrinkTasting",
                                                                     back_populates="tasting",
                                                                     cascade="all, delete-orphan",
                                                                     overlaps="drinks,tastings")
    drinks = relationship("Drink", secondary="drink_tasting_associations", back_populates="tastings",
                          lazy="selectin", overlaps="drink_associations,tasting,drink,tasting_associations")
    """


class BaseIngredient(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'baseingredient'
    plural_name = plural(single_name)


class Glassware(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'glassware'
    plural_name = plural(single_name)


class Scale(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'scale'
    plural_name = plural(single_name)


class Body(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'body'
    plural_name = plural(single_name)
