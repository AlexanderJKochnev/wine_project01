# app.core.service/service_layer.py

from typing import Optional, List, Any, TypeVar, Dict
from sqlalchemy.orm import DeclarativeMeta
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.models.base_model import Base
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class Service:
    def __init__(self, repositiory: Repository, model: Base):
        self.repository = repositiory
        self.model = model

    async def create(self, data: Dict[str, Any], session: AsyncSession) -> ModelType:
        """ create & return record """

        obj = self.model(**data)
        session.add(obj)
        await session.flush()  # в сложных запросах когда нужно получить id и добавиить его в связанную таблицу
        await session.commit()
        await session.refresh(obj)
        return obj


    async def search_in_main_table(self,
                                   query: str,
                                   page: int,
                                   page_size: int,
                                   session: AsyncSession) -> List[Any]:
        skip = (page - 1) * page_size
        return await self.repository.search_in_main_table(query, page, page_size, skip, session)