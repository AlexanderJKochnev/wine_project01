# app/core/schemas/image_mixin.py
from pydantic import BaseModel, computed_field
from typing import Optional
from app.core.config.project_config import settings


class ImageUrlMixin(BaseModel):
    """Pydantic миксин для автоматической генерации image_url из image_path"""

    image_path: Optional[str] = None  # Обязательно! Чтобы Pydantic знал, что это поле приходит из БД

    @computed_field
    @property
    def image_url(self) -> Optional[str]:
        """
        Генерирует полный URL изображения на основе image_path и BASE_URL из настроек.
        Если image_path пустой — возвращает None.
        """
        if not self.image_path:
            return None
        # Используем настройки (например, settings.API_BASE_URL или settings.IMAGE_BASE_URL)
        base_url = getattr(settings, "IMAGE_BASE_URL", "/images/")
        return f"{base_url.rstrip('/')}/{self.image_path.lstrip('/')}"