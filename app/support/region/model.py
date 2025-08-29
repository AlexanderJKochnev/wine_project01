# app/support/region/model.py
from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)
from typing import TYPE_CHECKING
from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt

if TYPE_CHECKING:
    from app.support.country.model import Country


class Region(Base, BaseLang, BaseEn, BaseAt):
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    country: Mapped["Country"] = relationship(back_populates="regions")

    drinks = relationship("Drink", back_populates="region")
