# app/support/tasting/model.py
from __future__ import annotations

from sqlalchemy.orm import Mapped, relationship

from typing import List, TYPE_CHECKING

# from sqlalchemy.orm import Mapped, relationship
from app.core.config.project_config import settings
from app.core.models.base_model import BaseFull, plural
from app.service_registry import registers_search_update

if TYPE_CHECKING:
    from app.support.drink.model import DrinkTastingNote, DrinkBaseIngredient


@registers_search_update("drink_associations.drink.items")
class TastingNote(BaseFull):
    table_description = 'Дегустация. Сравнительные вкусовые характеристики'
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'tastingnote'
    plural_name = plural(single_name)
    # Связь с промежуточной таблицей
    drink_associations: Mapped[List["DrinkTastingNote"]] = relationship(
        back_populates="tastingnote", cascade="all, delete-orphan"
    )


@registers_search_update("drink_associations.drink.items")
class BaseIngredient(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'baseingredient'
    plural_name = plural(single_name)
    # Связь с промежуточной таблицей
    drink_associations: Mapped[List["DrinkBaseIngredient"]] = relationship(
        back_populates="baseingredient", cascade="all, delete-orphan"
    )


@registers_search_update("drink.items")
class Glassware(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'glassware'
    plural_name = plural(single_name)
    drinks = relationship(
        "Drink", back_populates=single_name, cascade=cascade, lazy=lazy
    )


@registers_search_update("drink.items")
class Scale(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'scale'
    plural_name = plural(single_name)
    drinks = relationship(
        "Drink", back_populates=single_name, cascade=cascade, lazy=lazy
    )


@registers_search_update("drink.items")
class Body(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'body'
    plural_name = plural(single_name)
    drinks = relationship(
        "Drink", back_populates=single_name, cascade=cascade, lazy=lazy
    )
