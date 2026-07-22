# app.core.repositories.minhash_repository.py
import asyncio
from typing import List
from datasketch import MinHash


class MinHashSearchRepository:
    """
    Асинхронный репозиторий данных.
    Отвечает ТОЛЬКО за отправку запросов в драйвер и получение ответов.
    """

    def __init__(self, lsh_driver):
        self._lsh = lsh_driver
        # Гарантируем единый источник правды для num_perm напрямую из драйвера
        self.num_perm: int = lsh_driver.num_perm

    async def save(self, key: str, minhash: MinHash) -> None:
        """Асинхронное сохранение/обновление хэша в LSH драйвере."""
        def _sync_save():
            try:
                self._lsh.remove(key)
            except ValueError:
                pass
            self._lsh.insert(key, minhash)

        await asyncio.to_thread(_sync_save)

    async def delete(self, key: str) -> None:
        """Aсинхронное удаление хэша из LSH драйвера."""
        def _sync_delete():
            try:
                self._lsh.remove(key)
            except ValueError:
                pass

        await asyncio.to_thread(_sync_delete)

    async def find_similar(self, minhash: MinHash) -> List[str]:
        """Асинхронный запрос к LSH драйверу на поиск похожих ключей."""
        return await asyncio.to_thread(self._lsh.query, minhash)
