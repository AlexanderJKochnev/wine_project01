# app/support/region/models.py

from sqlalchemy import String, Text, text, ForeignKey, Column, Integer   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401
from typing import List


class Region(Base):
    """country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"), nullable=False)
    # Добавляем relationship
    country: Mapped["Country"] = relationship(back_populates="regions")  # noqa F821

    drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="region", cascade="all, delete-orphan")
    """
    country_id = Column(Integer, ForeignKey("countries.id"))
    # country = relationship("Country", back_populates="regions")
    # drinks = relationship("Drink", back_populates="region", lazy="select")
    
    country_id = Column(Integer, ForeignKey("countries.id"))
    country = relationship("Country", back_populates = "regions")
    drinks = relationship("Drink", back_populates = "region", lazy = "select")