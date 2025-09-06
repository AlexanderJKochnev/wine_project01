# app/support/country/model.py
from __future__ import annotations
from app.core.models.base_model import BaseFull
from sqlalchemy.orm import relationship
from app.core.config.project_config import settings
from app.core.utils.common_utils import plural

class Country(BaseFull):
    regions = relationship("Region", back_populates="country", lazy="selectin")

    # drinks = relationship("Drink", back_populates="category", lazy="select")