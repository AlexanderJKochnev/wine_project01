# app/support/subregion/model.py
from __future__ import annotations
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)
from typing import TYPE_CHECKING
from app.core.models.base_model import BaseFull
from app.core.config.project_config import settings
from app.core.utils.common_utils import plural

if TYPE_CHECKING:
    from app.support.country.model import Region


class Subregion(BaseFull):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    name = 'subregion'
    plural_name = plural(name)
    region_id: Mapped[int] = mapped_column(ForeignKey("regions.id"), nullable=False)
    region: Mapped["Region"] = relationship(back_populates=plural_name, lazy=lazy)

    drinks = relationship("Drink", back_populates=name,
                              cascade=cascade,
                              lazy=lazy)
