# app/core/config/database/db_config.py

from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
# from os import path
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings  # , SettingsConfigDict

load_dotenv()


class ConfigDataBase(BaseSettings):
    """ Postgresql Database Setting """
    # model_config = SettingsConfigDict(env_file=".env")
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    DB_ECHO_LOG: bool
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = Path('../.env')
        # env_file = ".env"

    @property
    def database_url(self) -> Optional[PostgresDsn]:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings_db = ConfigDataBase()


def get_db_url():
    return (
        f"postgresql+asyncpg://{settings_db.POSTGRES_USER}"
        f":{settings_db.POSTGRES_PASSWORD}@"
        f"{settings_db.POSTGRES_HOST}:{settings_db.POSTGRES_PORT}/"
        f"{settings_db.POSTGRES_DB}"
    )


def get_auth_data():
    return {"secret_key": settings_db.SECRET_KEY,
            "algorithm": settings_db.ALGORITHM}
