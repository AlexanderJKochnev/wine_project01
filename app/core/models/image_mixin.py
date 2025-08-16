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

    def get_image_url(self, base_url: str = "/images/") -> Optional[str]:
        """Получить URL изображения"""
        if self.image_path:
            return f"{base_url}{self.image_path}"
        return None

    def get_full_image_path(self) -> Optional[str]:
        """Получить полный путь к изображению на диске"""
        if self.image_path and hasattr(settings, 'UPLOAD_DIR'):
            return os.path.join(settings.UPLOAD_DIR, self.image_path)
        return None

    def has_image(self) -> bool:
        """Проверить, есть ли у объекта изображение"""
        return bool(self.image_path)
