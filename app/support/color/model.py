# app/support/color/model.py
from __future__ import annotations
from sqlalchemy.orm import (relationship)
from app.core.config.project_config import settings
from app.core.utils.common_utils import plural
from app.core.models.base_model import BaseFull


class Color(BaseFull):
    # Обратная связь: один ко многим
    """drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="color",
                                                 cascade="all, delete-orphan")
    """
    lazy = settings.LAZY
    cascade = settings.CASCADE
    name = 'color'
    plural_name = plural(name)
    drinks = relationship("Drink", back_populates=name,
                          cascade=cascade,
                          lazy=lazy)
