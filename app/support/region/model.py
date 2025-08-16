# app/support/region/model.py

from sqlalchemy import ForeignKey, Column, Integer
from sqlalchemy.orm import relationship
from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt


class Region(Base, BaseLang, BaseEn, BaseAt):
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
    country = relationship("Country", back_populates="regions")
    drinks = relationship("Drink", back_populates="region", lazy="select")
