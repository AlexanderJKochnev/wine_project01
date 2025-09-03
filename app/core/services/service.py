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

    async def create(self, data: ModelType, session: AsyncSession) -> ModelType:
        """ create & return record """
        # удаляет пустые поля
        data_dict = data.model_dump(exclude_unset=True)
        obj = self.model(**data_dict)
        return await self.repository.create(obj, session)

    async def get_by_id(self, id: int, session: AsyncSession) -> Optional[ModelType]:
        """
        get one record by id
        """
        obj = await self.repository.get_by_id(id, session)
        return obj

    async def get_all(self, page: int, page_size: int, session: AsyncSession, ) -> List[dict]:
        # Запрос с загрузкой связей и пагинацией
        skip = (page - 1) * page_size
        items, total = await self.repository.get_all(skip, page_size, session)
        result = {"items": items,
                  "total": total,
                  "page": page,
                  "page_size": page_size,
                  "has_next": skip + len(items) < total,
                  "has_prev": page > 1}
        return result

# -------------------
    async def search_in_main_table(self,
                                   query: str,
                                   page: int,
                                   page_size: int,
                                   session: AsyncSession) -> List[Any]:
        skip = (page - 1) * page_size
        return await self.repository.search_in_main_table(query, page, page_size, skip, session)