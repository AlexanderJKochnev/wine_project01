# app.core.service.search_service.py
"""
    сервис для нечеткого поиска minhash
    ищет с опечатками и огрмной скоростью (проверить)
    ищет похожие записи
"""

import asyncio
import re
import threading
from typing import List
import redis
from datasketch import MinHash, MinHashLSH


class MinHashSearchService:
    """
        Сервис нечеткого поиска, полностью изолированный от логики подключения.
        # threshold - порог схожести Жаккара (0.5 = совпадение текста на 50%)
        # num_perm - размер сигнатуры (128 чисел на строку - стандарт для баланса точности и памяти)
    """

    def __init__(self, redis_client: redis.Redis, threshold: float = 0.5, num_perm: int = 128):
        self._num_perm = num_perm
        self._write_lock = threading.Lock()

        # Инициализируем LSH, передавая готовый синхронный клиент
        self.lsh = MinHashLSH(
            threshold=threshold, num_perm=num_perm,
            storage_config={'type': 'redis', 'config': {'redis': redis_client}}
        )

    def _build_minhash(self, text: str) -> MinHash:
        m = MinHash(num_perm=self._num_perm)
        if not text:
            return m
        clean_text = re.sub(r'[^a-zа-я0-9\s]', '', text.lower())
        shingles = [clean_text[i:i + 4] for i in range(len(clean_text) - 3)]
        for shingle in shingles:
            m.update(shingle.encode('utf-8'))
        return m

    def update_index(self, entity_id: int, full_text: str) -> None:
        """Потокобезопасное синхронное обновление для BackgroundTasks."""
        new_hash = self._build_minhash(full_text)
        key = f"doc_{entity_id}"

        with self._write_lock:
            try:
                self.lsh.remove(key)
            except ValueError:
                pass
            self.lsh.insert(key, new_hash)

    async def search_similar(self, user_query: str) -> List[int]:
        """Асинхронный поиск без блокировки event loop."""
        if not user_query.strip():
            return []

        loop = asyncio.get_running_loop()
        query_hash = await loop.run_in_executor(None, self._build_minhash, user_query)
        matched_keys = await loop.run_in_executor(None, self.lsh.query, query_hash)

        return [int(key.split('_')[1]) for key in matched_keys]
