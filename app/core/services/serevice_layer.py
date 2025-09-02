# app.core.service/service_layer.py

from typing import Optional, List, Any
from app.core.repositories.sqlalchemy_repository import Repository
from app.core.models.base_model import Base
from sqlalchemy.ext.asyncio import AsyncSession
class Service:
    def __init__(self, repositiory: Repository, model: Base):
        self.repository = repositiory
        self.model = model

        async def search_in_main_table(self, query: Optional[str], session: AsyncSession) -> List[Any]:
            return await self.repository.search_in_main_table(query, session)