# app/support/color/model.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,              # noqa: F401
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import (Base, BaseLang, BaseEn, BaseAt,  # noqa: F401
                                        str_null_true, str_null_index)   # noqa: F401


class Color(Base, BaseLang, BaseEn, BaseAt):
    # Обратная связь: один ко многим
    """drinks: Mapped[List["Drink"]] = relationship("Drink",  # noqa F821
                                                 back_populates="color",
                                                 cascade="all, delete-orphan")
    """
    drinks = relationship("Drink", back_populates="color")
