# app/support/superfood/router.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.superfood.model import Superfood
from app.support.superfood.schemas import (SuperfoodCreate)


class SuperfoodRouter(BaseRouter):  # [SuperfoodCreate, SuperfoodUpdate, SuperfoodRead]):
    def __init__(self):
        super().__init__(
            model=Superfood,
            prefix="/superfoods",
        )

    async def create(self, data: SuperfoodCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def create_relation(self, data: SuperfoodCreate,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result
