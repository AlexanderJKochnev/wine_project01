# app/support/country/model.py
from __future__ import annotations

from sqlalchemy.orm import relationship

from app.core.models.base_model import BaseFull


class Country(BaseFull):
    regions = relationship("Region", back_populates="country", lazy="selectin", cascade="all, delete-orphan")
