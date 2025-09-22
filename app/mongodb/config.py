# app/mongodb/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends  # NOQA: F401
from typing import AsyncGenerator, Optional
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
        self.database = None

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


async def get_mongodb():
    return mongodb


async def get_database(mongodb_instance: MongoDB = Depends(get_mongodb)):
    if mongodb_instance.database is None:
        default_url = settings.mongo_url
        default_db = settings.MONGO_DATABASE
        # default_url = os.getenv("MONGO_URL", "mongodb://admin:admin@localhost:27027")
        # default_db = os.getenv("MONGO_DB", "files_db")
        await mongodb_instance.connect(default_url, default_db)
    return mongodb_instance.database


async def connect_to_mongo1():
    if mongodb.client is None:
        mongodb.client = AsyncIOMotorClient(settings.mongo_url,
                                            maxPoolSize=10,
                                            minPoolSize=5)
        mongodb.database = mongodb.client[settings.MONGO_DATABASE]
        print("Connected to MongoDB")


async def close_mongo_connection1():
    """Закрывает MongoDB соединение"""
    if mongodb.client:
        mongodb.client.close()
        mongodb.client = None
        mongodb.database = None


# Dependency для использования в роутерах
async def get_mongo_db1() -> AsyncGenerator:
    """
    Dependency для получения MongoDB database.
    Используется в роутерах через Depends.
    """
    if mongodb.client is None:
        await connect_to_mongo1()

    try:
        yield mongodb.database
    finally:
        # Note: Не закрываем соединение здесь!
        # Соединение остается в пуле для reuse
        pass
