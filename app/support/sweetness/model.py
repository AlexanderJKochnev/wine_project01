# app/support/sweetness/model.py

from sqlalchemy.orm import relationship
from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt


class Sweetness(Base, BaseLang, BaseEn, BaseAt):
    # Обратная связь: один ко многим
    """drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="sweetness",
                                                 cascade="all, delete-orphan")
    """
    drinks = relationship("Drink", back_populates="sweetness")
