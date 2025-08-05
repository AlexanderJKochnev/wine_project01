# app/core/config/project_config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.utils import get_path_to_root


class Settings(BaseSettings):
    """ Project Settings """
    DB_ECHO: bool
    PROJECT_NAME: str
    VERSION: str
    DEBUG: bool
    CORS_ALLOWED_ORIGINS: str
    PAGE_DEFAULT: int = 20
    PAGE_MIN: int = 0
    PAGE_MAX: int = 100
    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')


settings = Settings()

get_paging: dict = {'def': settings.PAGE_DEFAULT,
                    'min': settings.PAGE_MIN,
                    'max': settings.PAGE_MAX
                    }