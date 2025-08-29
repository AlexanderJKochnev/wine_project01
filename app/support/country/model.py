# app/support/country/model.py
from __future__ import annotations
from app.core.models.base_model import BaseFull
from sqlalchemy.orm import relationship


class Country(BaseFull):
    regions = relationship("Region", back_populates="country", lazy="select")

    # drinks = relationship("Drink", back_populates="category", lazy="select")