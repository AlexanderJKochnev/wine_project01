# app/support/varietal/auth.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.varietal.model import Varietal
from app.support.varietal.schemas import (VarietalCreate, VarietalCreateRelation)


class VarietalRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Varietal,
            prefix="/varietals",
        )

    async def create(self, data: VarietalCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def create_relation(self, data: VarietalCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result
