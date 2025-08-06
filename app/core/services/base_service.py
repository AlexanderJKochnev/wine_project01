# app/core/services/base_service.py

""" Base methods """
from app.core.schemas.base_schema import PyModel
from app.core.repositories.base_repository import AbstractRepository
from app.core.repositories.sqlalchemy_repo2 import ModelType

""" not implemented """


class BaseService:

    def __init__(self, repository: AbstractRepository) -> None:
        self.repository: AbstractRepository = repository

    async def create(self, model: PyModel) -> ModelType:
        return await self.repository.create(data=model.model_dump())

    async def update(self, pk: int, model: PyModel) -> ModelType:
        return await self.repository.update(data=model.model_dump(), id=pk)

    async def delete(self, pk: int) -> None:
        await self.repository.delete(id=pk)

    async def get(self, pk: int) -> ModelType:
        return await self.repository.get(id=pk)
