# app/core/config/project_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from typing import List
from app.core.utils.common_utils import get_path_to_root
from app.core.utils.common_utils import strtolist


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
    SECRET_KEY: str = 'gV64m9aIzFG4qpgVphvQbPQrtAO0nM-7YwwOvu0XPt5KJOjAy4AfgLkqJXYEt'
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 50
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    # IMAGES
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10  # * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: str = "png, jpg, jpeg, gif, webp"  # shall be converted to set
    # RELATIONSHIPS
    LAZY: str = 'selectin'
    CASCADE: str = 'all, delete-orphan'
    DJANGO_PORT: int = 8093
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str
    AUTH_PREFIX: str = 'auth'
    USER_PREFIX: str = 'user'
    IMAGES_PREFIX: str = 'images'
    FILES_PREFIX: str = 'files'
    MONGODB_PREFIX: str = 'mongodb'
    BASE_URL: str
    PORT: int
    # DEV 0 production, DEV 1 development
    DEV: int = 0
    API_PREFIX: str = 'api'
    JSON_FILENAME: str = 'data.json'
    # PREACT
    PREACT_PREFIX: str = 'preact'
    HANDBOOKS_PREFIX: str = 'handbooks'
    LANGS: str = 'en, ru, fr'
    DEFAULT_LANG: str = 'en'
    IDETAIL_VIEW: str = 'name, description'
    ILIST_VIEW: str = 'name'
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    # Cache settings
    CACHE_DEFAULT_EXPIRE: int = 300

    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    @property
    def DETAIL_VIEW(self) -> list:
        return strtolist(self.IDETAIL_VIEW)

    @property
    def LIST_VIEW(self) -> list:
        return strtolist(self.ILIST_VIEW)

    @property
    def LANGUAGES(self):
        return strtolist(self.LANGS)

    @property
    def max_file_size(self) -> int:
        return self.MAX_FILE_SIZE * 1024 * 1024

    @property
    def allowed_extensions(self) -> List[str]:
        return strtolist(self.ALLOWED_EXTENSIONS)

    @property
    def get_exclude_list(self) -> List[str]:
        return strtolist(self.EXCLUDE_LIST)


settings = Settings()

get_paging: dict = {'def': settings.PAGE_DEFAULT,
                    'min': settings.PAGE_MIN,
                    'max': settings.PAGE_MAX
                    }

# Создаем директорию для загрузок при запуске
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
