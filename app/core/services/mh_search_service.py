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
    def __init__(self, repository: MinHashSearchRepository):
        self._repo = repository

    def _prepare_minhash(self, text: str) -> MinHash:
        m = MinHash(num_perm=self._repo.num_perm)
        if not text:
            return m
        clean_text = re.sub(r'[^a-zа-я0-9\s]', '', text.lower())
        shingles = [clean_text[i:i + 4] for i in range(len(clean_text) - 3)]
        for shingle in shingles:
            m.update(shingle.encode('utf-8'))
        return m

    async def update_index(self, entity_id: int, full_text: str) -> None:
        minhash = self._prepare_minhash(full_text)
        await self._repo.save(f"doc_{entity_id}", minhash)

    async def search_similar(self, user_query: str) -> List[int]:
        if not user_query.strip():
            return []
        query_minhash = self._prepare_minhash(user_query)
        matched_keys = await self._repo.find_similar(query_minhash)
        return [int(key.split('_')[1]) for key in matched_keys]
