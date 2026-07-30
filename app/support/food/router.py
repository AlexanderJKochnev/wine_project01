# app/support/food/auth.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.food.model import Food
from app.support.food.schemas import (FoodCreate, FoodCreateRelation)


class FoodRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Food,
            prefix="/foods",
        )

    async def create(self, data: FoodCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def create_relation(self, data: FoodCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result
