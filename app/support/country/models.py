# app/support/country/models.py

from app.core.models.base_model import Base
from typing import List
from sqlalchemy.orm import (relationship, Mapped, mapped_column)


class Country(Base):
    """regions: Mapped[List["Region"]] = relationship("Region",  # noqa F821
                                                   back_populates="country", cascade="all, delete-orphan")"""
    regions = relationship("Region", back_populates="country", lazy="select")
