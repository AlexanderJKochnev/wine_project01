# app.core.repositories.minhash_repository.py
from typing import List
from datasketch import MinHash


class MinHashSearchRepository:
    """Глупый асинхронный репозиторий. Только I/O операции."""

    def __init__(self, lsh_driver):
        self._lsh = lsh_driver
        # Источник правды для num_perm берется строго из переданного драйвера
        self.num_perm: int = lsh_driver.num_perm

    async def save(self, key: str, minhash: MinHash) -> None:
        """Нативная асинхронная вставка."""
        try:
            await self._lsh.remove(key)
        except ValueError:
            pass
        await self._lsh.insert(key, minhash)  # Нативный await библиотеки!

    async def delete(self, key: str) -> None:
        try:
            await self._lsh.remove(key)
        except ValueError:
            pass

    async def find_similar(self, minhash: MinHash) -> List[str]:
        """Нативный асинхронный поиск."""
        return await self._lsh.query(minhash)
