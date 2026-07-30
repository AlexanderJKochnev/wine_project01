# app.core.config.databse.redis_async.py

from typing import Optional
from redis.asyncio import ConnectionPool, Redis as AsyncRedis

from app.core.config.project_config import settings
from loguru import logger


class RedisManager:
    def __init__(self):
        self._host: str = settings.REDIS_HOST
        self._port: int = settings.REDIS_PORT
        self._password: str = settings.REDIS_PWD
        self._threshold: float = settings.SIMILARITY_THRESHOLD
        self._num_perm: int = settings.NUM_PERM
        self.pool: Optional[ConnectionPool] = None

    async def connect(self):
        """Асинхронная инициализация пула и проверка связи"""
        self.pool = ConnectionPool(
            host=self._host,
            port=self._port,
            password=self._password,
            db=0,
            decode_responses=False,  # False для работы со сжатыми (bytes) данными
            max_connections=20  # подбор - зависит от количества асинхронных задач
        )
        # Проверка: создаем временный клиент и пингуем базу
        async_client = AsyncRedis(connection_pool=self.pool)
        try:
            await async_client.ping()
            logger.info("✅ Redis connected successfully")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise e

    async def disconnect(self):
        """Асинхронное закрытие всех соединений"""
        if self.pool:
            await self.pool.disconnect()
            logger.info("🛑 Redis pool disconnected")

    def get_async_client(self) -> AsyncRedis:
        """Возвращает асинхронный клиент для эндпоинтов (кэш, сессии)."""
        if not self.pool:
            raise RuntimeError("Redis pool is not initialized")
        return AsyncRedis(connection_pool=self.pool)
