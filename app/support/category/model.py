# app/support/category/model.py
from __future__ import annotations
from sqlalchemy.orm import relationship
from app.core.models.base_model import BaseFull
from app.core.config.project_config import settings
from app.core.utils.common_utils import plural


class Category(BaseFull):
    lazy = settings.LAZY
    name = 'category'
    plural_name = plural(name)
    cascade = settings.CASCADE
    # Обратная связь: один ко многим
    drinks = relationship(
        "Drink", back_populates=name, cascade=cascade, lazy=lazy
    )
