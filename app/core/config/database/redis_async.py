# app.core.config.databse.redis_async.py
import redis
from datasketch import MinHashLSH
from redis.asyncio import ConnectionPool as AsyncConnectionPool, Redis as AsyncRedis
# синхронный redis только для datascetch
from app.core.config.project_config import settings
from loguru import logger


class RedisManager:
    def __init__(self):
        self.pool: AsyncConnectionPool = None
        self._host: str = settings.REDIS_HOST
        self._port: int = settings.REDIS_PORT
        self._password: str = settings.REDIS_PWD
        self._threshold: float = settings.SIMILARITY_THRESHOLD
        self._num_perm: int = settings.NUM_PERM
        self.lsh_driver: MinHashLSH = None

    async def connect(self):
        """Асинхронная инициализация пула и проверка связи"""
        self.pool = AsyncConnectionPool(
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

    def init_lsh_driver(self) -> None:
        """
        Метод независимой инициализации драйвера нечеткого поиска.
        Использует явный импорт хранилища, полностью защищенный от KeyError.
        """
        try:
            logger.info("⏳ Инициализация драйвера MinHashLSH...")

            # 1. Импортируем бэкенд-класс напрямую, обходя баги автоимпорта datasketch
            # from datasketch.storage import RedisStorage

            # 2. Создаем конфигурационный словарь для встроенного плагина
            storage_config = {'type': 'redis',
                              'redis': {'host': self._host, 'port': self._port,
                                        'password': self._password, 'db': 0},
                              "redis_buffer": {"transaction": True}}
            storage_config = {"type": "redis", "basename": b"my_lsh_index",  # опционально, для уникальности ключей
                              "redis": {"host": self._host, "port": self._port, "password": self._password, "db": 0, }}

            # Инициализируем MinHashLSH с storage_config
            self.lsh_driver = MinHashLSH(
                threshold=self._threshold, num_perm=self._num_perm, storage_config=storage_config
            )
            logger.info("✅ Redis Manager: Драйвер MinHashLSH успешно развернут")

        except Exception as e:
            logger.error(f"⚠️ Не удалось инициализировать MinHashLSH: {e}. Поиск временно недоступен.")
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

    def get_search_driver_client(self) -> redis.Redis:
        """
        ФАБРИКА КЛИЕНТА: Создает и настраивает специфичного клиента-драйвера.
        Репозиторий получит этот объект как абстрактный 'клиент базы данных'.
        """
        return redis.Redis(
            host=self._host, port=self._port, password=self._password, db=0, decode_responses=False
        )
