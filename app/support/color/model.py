# app/support/color/model.py
from __future__ import annotations

from app.core.config.project_config import settings
from app.core.models.base_model import BaseFull
from app.core.utils.common_utils import plural


class Color(BaseFull):

    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'color'
    plural_name = plural(single_name)
    """
    drinks = relationship("Drink", back_populates=single_name,
                          cascade=cascade,
                          lazy=lazy)
    """
