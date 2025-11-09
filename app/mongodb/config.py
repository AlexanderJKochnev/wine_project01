# app/mongodb/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends  # NOQA: F401
from typing import Optional
from app.core.utils.common_utils import get_path_to_root
# import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_path_to_root(), env_file_encoding='utf-8', extra='ignore'
    )
    MONGODB_CONTAINER_NAME: str
    MONGO_INITDB_ROOT_USERNAME: str
    MONGO_INITDB_ROOT_PASSWORD: str
    MONGO_INITDB_DATABASE: str
    MONGO_DATABASE: str
    MONGO_IMAGES: str = "images"
    MONGO_DOCUMENTS: str = "documents"
    MONGO_OUT_PORT: int = 27017
    MONGO_INN_PORT: int = 27017
    MONGO_HOSTNAME: str
    MONGO_EXPRESS_CONTAINER_NAME: str
    ME_CONFIG_MONGODB_ADMINUSERNAME: str
    ME_CONFIG_MONGODB_ADMINPASSWORD: str
    ME_CONFIG_MONGODB_SERVER: str
    ME_CONFIG_BASICAUTH_USERNAME: str
    ME_CONFIG_BASICAUTH_PASSWORD: str
    ME_OUT_PORT: int
    ME_INN_PORT: int
    # IMAGE SIZING в пикселях
    IMAGE_WIDTH: int
    IMAGE_HEIGH: int
    IMAGE_QUALITY: int
    LENGTH_RANDOM_NAME: int
    PAGE_DEFAULT: int
    PAGE_MIN: int
    PAGE_MAX: int

    @property
    def mongo_url(self) -> str:
        return (f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:"
                f"{self.MONGO_INITDB_ROOT_PASSWORD}@{self.MONGO_HOSTNAME}:"
                f"{self.MONGO_INN_PORT}")  # {self.MONGO_INITDB_DATABASE}")


settings = Settings()
# MONGO_URL = "mongodb://admin:admin@mongodb:27017"
# DATABASE_NAME = "files_db"


class MongoDB:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

    async def connect(self, connection_string: str, database_name: str):
        if self.client is None:
            self.client = AsyncIOMotorClient(connection_string)
            self.database = self.client[database_name]

    async def disconnect(self):
        if self.client:
            self.client.close()
            self.client = None
            self.database = None


mongodb = MongoDB()


# зависимость client+database для использования в роутах
async def get_mongodb():
    return mongodb


# зависимость только database для использования в роутах
async def get_database(mongodb_instance: MongoDB = Depends(get_mongodb)):
    if mongodb_instance.database is None:
        default_url = settings.mongo_url
        default_db = settings.MONGO_DATABASE
        # default_url = os.getenv("MONGO_URL", "mongodb://admin:admin@localhost:27027")
        # default_db = os.getenv("MONGO_DB", "files_db")
        await mongodb_instance.connect(default_url, default_db)
    return mongodb_instance.database
