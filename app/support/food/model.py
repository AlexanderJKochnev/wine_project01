# app/support/food/model.py

from app.core.models.base_model import Base, BaseLang, BaseEn, BaseAt

from sqlalchemy.orm import relationship


class Food(Base, BaseLang, BaseEn, BaseAt):
    """drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="food", cascade="all, delete-orphan")
    """
    drinks = relationship("Drink", back_populates="food", lazy="select")
