# app/core/config/database/db_amongo.py
# асинхронное соедиение с mongodb
from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import Depends, HTTPException
import os
from app.core.config.database.mongo_config import settings

# Настройки подключения
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://admin:password@localhost:27017/admin")
DATABASE_NAME = settings.MONGODB_DATABASE
HOST = f'localhost:{settings.MONGODB_PORT}'

_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None


# --- Фабрика клиента ---
async def get_mongo_client(username: str = settings.MONGODB_USER_NAME,
                           password: str = settings.MONGODB_USER_PASSWORD,
                           authSource: str = 'admin',
                           replicaSet: str = 'rs0',
                           maxPoolSize: int = 10,
                           minPoolSize: int = 5,
                           directConnection: bool = True,
                           # uuidRepresentation="standard"
                           ) -> AsyncIOMotorClient:
    """
    Создаёт и возвращает клиент MongoDB.
    Можно внедрить в зависимости, если нужен доступ к клиенту.
    """
    global _client
    if _client is None:
        # Используем directConnection=true для подключения к Replica Set с хоста
        _client = AsyncIOMotorClient(
            HOST,
            username=username,
            password=password,
            authSource=authSource,
            replicaSet=replicaSet,
            maxPoolSize=maxPoolSize,
            minPoolSize=minPoolSize,
            directConnection=directConnection,
            # uuidRepresentation=uuidRepresentation
        )
    return _client


# --- Фабрика базы данных ---
async def get_mongodb() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Зависимость для получения базы данных.
    Используется в эндпоинтах через Depends.
    """
    global _db
    if _db is None:
        client = await get_mongo_client()
        _db = client[DATABASE_NAME]
    try:
        yield _db
    except Exception as e:
        # Логирование (здесь упрощённо)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

# -------------------------------


async def get_mongo_client1():
    try:
        client = AsyncIOMotorClient(f'localhost:{settings.MONGODB_PORT}',
                                    username=settings.MONGODB_USER_NAME,
                                    password=settings.MONGODB_USER_PASSWORD,
                                    authSource='admin',
                                    replicaSet='rs0',
                                    maxPoolSize=10,
                                    minPoolSize=5,
                                    directConnection=True)
        # Проверяем соединение
        # await client.admin.command('ping')
        return client
    except Exception as e:
        print(f'Ошибка соединения с MongoDB: {e}')
    finally:
        if client:
            client.close()