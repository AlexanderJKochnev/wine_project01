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
    _repo = None
    BATH_SIZE = settings.MINHASH_BATCH_SIZE
    CLEAN_RE = re.compile(r'[^a-zа-я0-9\s]')
    num_perm = settings.NUM_PERM
    shingle = settings.SHINGLE

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


class MinHashCreateIndex(MinHashRootService):
    """
        run_sync_background:            запуск фонового создания индекса
    """

    def __init__(self, lsh_driver, model_name: str = 'Item',
                 field_name: str = 'search_content'):
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
                # session = self._session
                # Получаем асинхронный генератор (курсор) из Postgres-репозитория
                db_stream: AsyncGenerator[Tuple[int, str], None] = self.stream_all_search_data(self.model_name,
                                                                                               self.field_name,
                                                                                               self.BATH_SIZE,
                                                                                               session)

                while True:
                    # 1. МОЛНИЕНОСНО забираем 5000 строк из сетевого буфера Postgres
                    # База данных сразу понимает, что мы активны, и таймаут сбрасывается
                    chunk: List[Tuple[int, str]] = []

                    async for entity_id, full_text in db_stream:
                        if full_text:
                            chunk.append((entity_id, full_text))
                        if len(chunk) >= self.BATCH_SIZE:
                            break  # Выходим из итератора, давая Postgres передышку
                    # Если данных больше нет — выходим из основного цикла
                    if not chunk:
                        break

                    # 2. И только ПОСЛЕ того, как пачка уже лежит в памяти Python,
                    # мы запускаем тяжелую обработку и отправку хэшей в Redis
                    tasks = [self._index_single_record(lsh_driver, eid, text) for eid, text in chunk]
                    await asyncio.gather(*tasks)

                    # Очищаем память
                    chunk.clear()

                    # Небольшая микро-пауза, чтобы дать Event Loop обработать другие задачи API
                    await asyncio.sleep(0.01)

                logger.info("✅ Асинхронный прогрев базы хэшей успешно завершен!")

            except Exception as e:
                logger.error(f"❌ Критическая ошибка во время фонового прогрева: {e}")
            finally:
                await session.close()

    async def stream_all_search_data(self,
                                     model_name: str,
                                     field_name: str, chunk: int,
                                     session: AsyncSession
                                     ) -> AsyncGenerator[Tuple[int, str], None]:
        """
        стриминг агрегированных текстовых данных.
        Использует серверный курсор через yield_per для удержания памяти RAM в пределах нормы.
        """
        model = get_model_by_name('Item')
        # 1. Формируем базовый запрос
        # chunk = 5000 заставляем SQLAlchemy запрашивать данные у драйвера именно такими пачками
        if not hasattr(model, field_name):
            raise AttributeError(f"Model {model.__name__} has no attribute '{field_name}'")
        field_attr = getattr(model, field_name)
        query = (select(model.id, field_attr)
                 .where(field_attr.isnot(None), field_attr != '')
                 .order_by(model.id))
        # 2. Запускаем асинхронный стрим через специальный метод сессии
        result_stream = await session.stream(
            query.execution_options(yield_per=chunk)
        )
        # 3. Лениво итерируемся по строкам из сетевого буфера драйвера
        async for row in result_stream:
            # row - объект SQLAlchemy, распаковываем в Tuple
            entity_id, full_text = row
            yield entity_id, full_text


class MinHashSearchService(MinHashRootService):
    def __init__(self, repository: MinHashSearchRepository):
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
