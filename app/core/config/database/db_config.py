# app/core/config/database/db_config.py

from typing import Optional
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core.utils import get_path_to_root

# load_dotenv() - не использовать - путает


class ConfigDataBase(BaseSettings):
    """ Postgresql Database Setting """
    model_config = SettingsConfigDict(env_file=get_path_to_root(),
                                      env_file_encoding='utf-8',
                                      extra='ignore')

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DB_ECHO_LOG: bool
    # probable secirity issue:
    SECRET_KEY: str
    ALGORITHM: str

    @property
    def database_url(self) -> Optional[PostgresDsn]:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings_db = ConfigDataBase()


def get_auth_data():
    return {"secret_key": settings_db.SECRET_KEY,
            "algorithm": settings_db.ALGORITHM}
