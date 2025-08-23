# app/support/category/model.py
from __future__ import annotations
from sqlalchemy.orm import relationship
from app.core.models.base_model import BaseFull


class Category(BaseFull):
    # Обратная связь: один ко многим
    drinks = relationship("Drink", back_populates="category", lazy="select")
