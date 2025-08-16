# app/core/config/project_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from app.core.utils.common_utils import get_path_to_root


class Settings(BaseSettings):
    """ Project Settings """
    DB_ECHO: bool
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    CORS_ALLOWED_ORIGINS: str
    # PAGING
    PAGE_DEFAULT: int = 20
    PAGE_MIN: int = 0
    PAGE_MAX: int = 100
    # AUTHORIZATIOON
    SECRET_KEY: str
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 50
    # IMAGES
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10  # * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = "png, jpg, jpeg, gif, webp"  # shall be converted to set

    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    @property
    def max_file_size(self) -> int:
        return self.MAX_FILE_SIZE * 1024 * 1024

    @property
    def allowed_extensions(self) -> str:
        return {a.strip() for a in self.ALLOWED_EXTENSIONS.split(',')}


settings = Settings()

get_paging: dict = {'def': settings.PAGE_DEFAULT,
                    'min': settings.PAGE_MIN,
                    'max': settings.PAGE_MAX
                    }

# Создаем директорию для загрузок при запуске
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
