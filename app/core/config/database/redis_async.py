# app.core.config.databse.redis_async.py

from typing import Optional
from redis.asyncio import ConnectionPool, Redis as AsyncRedis
from datasketch.aio import AsyncMinHashLSH  # Нативный асинхронный драйвер

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
        self.lsh_driver: Optional[AsyncMinHashLSH] = None

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

    async def init_lsh_driver(self) -> None:
        """
        Асинхронная инициализация тяжелого драйвера поиска.
        Использует aioredis/redis.asyncio бэкенд из общего пула.
        """
        try:
            logger.info("⏳ Инициализация асинхронного драйвера AsyncMinHashLSH...")

            # Получаем асинхронного клиента из нашего пула
            shared_async_client = self.get_async_client()

            # Конфигурация для асинхронного бэкенда datasketch
            storage_config = {'type': 'aioredis',  # В асинхронном модуле тип называется aioredis
                              'redis': {'redis': shared_async_client}}

            self.lsh_driver = await AsyncMinHashLSH(
                threshold=self._threshold, num_perm=self._num_perm, storage_config=storage_config
            )
            logger.info("✅ Redis Manager: Драйвер AsyncMinHashLSH успешно развернут")
        except Exception as e:
            logger.error(f"⚠️ Ошибка инициализации AsyncMinHashLSH: {e}. Поиск отключен.")
            self.lsh_driver = None

    def disable_lsh_driver(self) -> None:
        """Метод для динамического отключения поиска 'на лету' без остановки Redis."""
        self.lsh_driver = None
        logger.warning("🛑 Драйвер MinHashLSH отключен. Поисковые функции деактивированы.")

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

    def get_lsh_driver(self) -> AsyncMinHashLSH:
        if not self.lsh_driver:
            raise RuntimeError("Драйвер AsyncMinHashLSH в данный момент отключен.")
        return self.lsh_driver
