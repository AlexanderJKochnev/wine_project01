# app.core.service.search_service.py
"""
    сервис для нечеткого поиска minhash
    ищет с опечатками и огрмной скоростью (проверить)
    ищет похожие записи
"""
import asyncio
import re

from loguru import logger
from typing import AsyncGenerator, List, Tuple
from datasketch import MinHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import DatabaseManager
from app.core.config.project_config import settings
from app.core.models.base_model import get_model_by_name
from app.core.repositories.minhash_repository import MinHashSearchRepository


class MinHashRootService:
    """
        базовый класс для MinHashSearchService и MinHashCreateIndex
        содержит общие переменные и методы
    """

    def __init__(self):
        self._repo = None
        self.BATCH_SIZE = settings.MINHASH_BATCH_SIZE
        self.CLEAN_RE = re.compile(r'[^a-zа-я0-9\s]')
        self.num_perm = settings.NUM_PERM
        self.shingle = settings.SHINGLE

    def _prepare_minhash(self, text: str) -> MinHash:
        """
            преобразование текста в minhash shingles
        """
        m = MinHash(num_perm=self.num_perm)
        if not text:
            return m
        clean_text = self.CLEAN_RE.sub('', text.lower())
        shingles = [clean_text[i:i + self.shingle] for i in range(len(clean_text) - self.shingle + 1)]
        for shingle in shingles:
            m.update(shingle.encode('utf-8'))
        return m


def _sync_process_chunk(chunk: List[Tuple[int, str]], root_service: MinHashRootService) -> List[Tuple[str, MinHash]]:
    """
        Синхронный пакетный расчет хэшей в фоновом потоке ОС.
        Разгружает Event Loop, предотвращая зависание FastAPI при старте.
    """
    processed = []
    for entity_id, full_text in chunk:
        minhash = root_service._prepare_minhash(full_text)
        processed.append((f"doc_{entity_id}", minhash))
    return processed


class MinHashCreateIndex(MinHashRootService):
    """
        run_sync_background:            запуск фонового создания индекса
    """

    def __init__(self, lsh_driver, model_name: str = 'Item',
                 field_name: str = 'search_content'):
        super().__init__()
        self.lsh_driver = lsh_driver
        self.model_name = model_name
        self.field_name = field_name

    async def _index_single_record(self, lsh_driver, entity_id: int, full_text: str) -> None:
        minhash = self._prepare_minhash(full_text)
        key = f"doc_{entity_id}"
        try:
            await lsh_driver.remove(key)
        except ValueError:
            pass
        await lsh_driver.insert(key, minhash)

    async def execute_heavy_warmup(self) -> None:
        """
        Безопасный воркер прогрева.
        Разрывает связь между скоростью чтения из Postgres и скоростью записи в Redis.
        """
        async with DatabaseManager.session_maker() as session:
            try:
                logger.warning("⚠️ Поисковый индекс пуст. Запуск безопасного фонового прогрева...")
                lsh_driver = self.lsh_driver

                # Безопасно получаем асинхронный клиент Redis из драйвера для работы с пайплайнами
                async_redis_client = lsh_driver.storage.keys_keys

                db_stream: AsyncGenerator[Tuple[int, str], None] = self.stream_all_search_data(
                    self.model_name, self.field_name, self.BATCH_SIZE, session
                )

                while True:
                    # 1. МОЛНИЕНОСНО забираем 5000 строк из сетевого буфера Postgres
                    chunk: List[Tuple[int, str]] = []

                    async for entity_id, full_text in db_stream:
                        if full_text:
                            chunk.append((entity_id, full_text))
                        if len(chunk) >= self.BATCH_SIZE:
                            break  # Выходим из итератора, давая Postgres передышку

                    # Если данных больше нет — выходим из основного цикла
                    if not chunk:
                        break

                    # 2. ПАРАЛЛЕЛИЗМ: Выносим тяжелый CPU-расчет хэшей пачки в отдельный поток ОС.
                    # Основной поток FastAPI свободен и мгновенно отвечает клиентам.
                    hashed_chunk = await asyncio.to_thread(_sync_process_chunk, chunk, self)

                    # 3. КОНВЕЙЕРИЗАЦИЯ (Защита от Error 99): Пишем всю пачку одним сетевым пакетом
                    async with async_redis_client.pipeline(transaction=False) as pipe:
                        for key, minhash in hashed_chunk:
                            try:
                                await lsh_driver.remove(key, p=pipe)
                            except ValueError:
                                pass
                            await lsh_driver.insert(key, minhash, p=pipe)

                        # Выстрел пакета команд в сеть Redis
                        await pipe.execute()

                    # Очищаем память, помогая Garbage Collector
                    chunk.clear()
                    hashed_chunk.clear()

                    # Небольшая микро-пауза, чтобы дать Event Loop обработать другие задачи API
                    await asyncio.sleep(0.001)

                logger.info("✅ Асинхронный прогрев базы хэшей успешно завершен!")

            except Exception as e:
                logger.error(f"❌ Критическая ошибка во время фонового прогрева: {e}")
            finally:
                await session.close()

    async def stream_all_search_data(
            self, model_name: str, field_name: str, chunk: int, session: AsyncSession
    ) -> AsyncGenerator[Tuple[int, str], None]:
        """
        стриминг агрегированных текстовых данных.
        Использует серверный курсор через yield_per для удержания памяти RAM в пределах нормы.
        """
        model = get_model_by_name(model_name)

        if not hasattr(model, field_name):
            raise AttributeError(f"Model {model.__name__} has no attribute '{field_name}'")

        field_attr = getattr(model, field_name)
        query = (select(model.id, field_attr).where(field_attr.isnot(None), field_attr != '').order_by(model.id))

        # Запускаем асинхронный стрим с передачей yield_per через параметры исполнения
        result_stream = await session.stream(
            query.execution_options(yield_per=chunk)
        )

        # Лениво итерируемся по строкам
        async for row in result_stream:
            # Безопасная распаковка строки SQLAlchemy 2.0 без обращения по индексам
            entity_id, full_text = row
            yield entity_id, full_text


class MinHashSearchService(MinHashRootService):
    def __init__(self, repository: MinHashSearchRepository):
        super().__init__()
        self._repo = repository

    async def update_index(self, entity_id: int, full_text: str) -> None:
        minhash = self._prepare_minhash(full_text)
        await self._repo.save(f"doc_{entity_id}", minhash)

    async def search_similar(self, user_query: str) -> List[int]:
        if not user_query.strip():
            return []
        query_minhash = self._prepare_minhash(user_query)
        matched_keys = await self._repo.find_similar(query_minhash)
        return [int(key.split('_')[1]) for key in matched_keys]
