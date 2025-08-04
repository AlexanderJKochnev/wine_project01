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

    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')


settings = Settings()
