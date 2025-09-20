# app/mongodb/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends  # NOQA: F401
from typing import AsyncGenerator
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

    @property
    def mongo_url(self) -> str:
        return (f"mongodb://{self.MONGO_INITDB_ROOT_USERNAME}:"
                f"{self.MONGO_INITDB_ROOT_PASSWORD}@{self.MONGO_HOSTNAME}:"
                f"{self.MONGO_INN_PORT}")  # {self.MONGO_INITDB_DATABASE}")


settings = Settings()
# MONGO_URL = "mongodb://admin:admin@mongodb:27017"
# DATABASE_NAME = "files_db"


async def mongo_client():
    """ Cинхронное соединение с базой данных """
    # uri = 'mongodb://root:example@localhost'
    client = AsyncIOMotorClient(settings.mongo_url)
    yield client
    client.close()

# ------------------

class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    if mongodb.client is None:
        mongodb.client = AsyncIOMotorClient(settings.mongo_url,
                                            maxPoolSize=10,
                                            minPoolSize=5)
        mongodb.database = mongodb.client[settings.MONGO_DATABASE]
        print("Connected to MongoDB")


async def close_mongo_connection():
    """Закрывает MongoDB соединение"""
    if mongodb.client:
        mongodb.client.close()
        mongodb.client = None
        mongodb.database = None


# Dependency для использования в роутерах
async def get_mongo_db() -> AsyncGenerator:
    """
    Dependency для получения MongoDB database.
    Используется в роутерах через Depends.
    """
    if mongodb.client is None:
        await connect_to_mongo()

    try:
        yield mongodb.database
    finally:
        # Note: Не закрываем соединение здесь!
        # Соединение остается в пуле для reuse
        pass
