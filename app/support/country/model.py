# app/support/country/model.py

from app.core.models.base_model import Base
from sqlalchemy.orm import relationship


class Country(Base):
    """regions: Mapped[List["Region"]] = relationship("Region",  # noqa F821
                                                   back_populates="country", cascade="all, delete-orphan")"""
    regions = relationship("Region", back_populates="country", lazy="select")
