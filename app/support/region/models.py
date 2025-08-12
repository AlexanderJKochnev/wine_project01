# app/support/region/models.py

from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401


class Region(Base):
    country_id: Mapped[int] = mapped_column(
        ForeignKey("countries.id"), nullable=False)
    # Добавляем relationship
    country: Mapped["Country"] = relationship(back_populates="regions")  # noqa F821
