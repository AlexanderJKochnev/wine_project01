# app/core/models/image_mixin.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, TYPE_CHECKING
import os
from app.core.config.project_config import settings

if TYPE_CHECKING:
    from app.core.models.base_model import Base  # noqa: F401


class ImageMixin:
    """Mixin для добавления функционала изображений к моделям"""

    image_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
