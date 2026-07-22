# app.core.config.databse.redis_async.py
from redis.asyncio import ConnectionPool as AsyncConnectionPool, Redis as AsyncRedis
# синхронный redis только для datascetch
from redis import Redis
from app.core.config.project_config import settings
from loguru import logger


class RedisManager:
    def __init__(self):
        self.pool: AsyncConnectionPool = None
        self._host = None
        self._port = None
        self._password = None

    async def connect(self, host: str, port: int):
        """Асинхронная инициализация пула и проверка связи"""
        host = settings.REDIS_HOST
        port = settings.REDIS_PORT
        password = settings.REDIS_PWD
        self.pool = AsyncConnectionPool(
            host=host,
            port=port,
            password=password,
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

    def get_client(self) -> Redis:
        """Возвращает готовый клиент, привязанный к пулу"""
        return Redis(connection_pool=self.pool)

    def get_sync_client(self) -> Redis:
        """
        Возвращает синхронный клиент, настроенный на те же параметры.
        Он будет создаваться на лету внутри сервиса для datasketch.
        """
        return Redis(
            host=self._host,
            port=self._port,
            password=self._password,
            db=0,
            decode_responses=False
        )
