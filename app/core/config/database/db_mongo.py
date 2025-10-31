# app/core/config/database/db_amongo.py
# не используется проверить и удалтить

from typing import AsyncGenerator
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from fastapi import HTTPException
from app.core.config.database.mongo_config import settings
# --- Глобальные переменные ---
_client: AsyncIOMotorClient | None = None


# --- Фабрика клиента ---
async def get_mongo_client() -> AsyncIOMotorClient:
    """
    Возвращает единый экземпляр AsyncIOMotorClient.
    Использует те же параметры, что и в рабочих тестах.
    """
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(
            host='localhost',  # например, 'localhost'
            port=settings.MONGODB_PORT,  # например, 27019
            username=settings.MONGODB_USER_NAME,
            password=settings.MONGODB_USER_PASSWORD,
            authSource='admin',
            # replicaSet=settings.MONGODB_REPLICA_SET,  # 'rs0'
            directConnection=True,  # 🔥 Критично: иначе — ошибка с DNS
            maxPoolSize=10,
            minPoolSize=5,
            serverSelectionTimeoutMS=10000,
            uuidRepresentation="standard"
        )
        # Проверяем подключение
        try:
            await _client.admin.command("ping")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to MongoDB: {e}")
    return _client


# --- Фабрика базы данных ---
async def get_mongodb() -> AsyncGenerator[AsyncIOMotorDatabase, None]:
    """
    Зависимость для получения базы данных.
    Используется в FastAPI-роутах через Depends.
    """
    client = await get_mongo_client()
    db = client[settings.MONGODB_DATABASE_NAME]
    try:
        yield db
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
