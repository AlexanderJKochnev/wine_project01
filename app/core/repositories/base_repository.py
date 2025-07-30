# app/core/repositories/base_repository.py

from abc import ABC, abstractmethod
""" Abstract Base repository class """


class AbstractRepository(ABC):

    @abstractmethod
    async def create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_single(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, **kwargs):
        raise NotImplementedError
