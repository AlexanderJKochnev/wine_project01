# app.core.service.search_service.py
"""
    сервис для нечеткого поиска minhash
    ищет с опечатками и огрмной скоростью (проверить)
    ищет похожие записи
"""
import re
from typing import List
from datasketch import MinHash

from app.core.repositories.minhash_repository import MinHashSearchRepository


class MinHashSearchService:
    """
    Сервисный слой бизнес-логики.
    Отвечает за подготовку данных (парсинг, шинглы, MinHash) и работу с репозиторием.
    """

    def __init__(self, repository: MinHashSearchRepository):
        self._repo = repository

    def _prepare_minhash(self, text: str) -> MinHash:
        """Бизнес-логика: нормализация текста и построение MinHash сигнатуры."""
        # Берем num_perm из репозитория (который взял его из драйвера)
        m = MinHash(num_perm=self._repo.num_perm)
        if not text:
            return m

        # Очистка текста от мусора
        clean_text = re.sub(r'[^a-zа-я0-9\s]', '', text.lower())

        # Нарезка на 4-граммы символов
        shingles = [clean_text[i:i + 4] for i in range(len(clean_text) - 3)]

        for shingle in shingles:
            m.update(shingle.encode('utf-8'))
        return m

    async def update_index(self, entity_id: int, full_text: str) -> None:
        """Бизнес-логика обновления индекса для сущности."""
        minhash = self._prepare_minhash(full_text)
        key = f"doc_{entity_id}"
        await self._repo.save(key, minhash)

    async def remove_from_index(self, entity_id: int) -> None:
        """Бизнес-логика удаления сущности из индекса."""
        key = f"doc_{entity_id}"
        await self._repo.delete(key)

    async def search_similar(self, user_query: str) -> List[int]:
        """Бизнес-логика нечеткого поиска."""
        if not user_query.strip():
            return []

        query_minhash = self._prepare_minhash(user_query)

        # Вызываем полностью асинциированный метод репозитория
        matched_keys = await self._repo.find_similar(query_minhash)

        # Конвертируем строковые ключи драйвера в понятные для Postgres ID
        return [int(key.split('_')[1]) for key in matched_keys]
