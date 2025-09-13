# app/support/food/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.food.model import Food
from app.support.food.repository import FoodRepository
from app.support.food.schemas import FoodRead, FoodCreate, FoodUpdate, FoodCreateRelation
from app.support.food.service import FoodService


class FoodRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Food,
            repo=FoodRepository,
            create_schema=FoodCreate,
            patch_schema=FoodUpdate,
            read_schema=FoodRead,
            prefix="/foods",
            tags=["foods"],
            service=FoodService,
            create_schema_relation=FoodCreateRelation
        )

    async def create(self, data: FoodCreate, session: AsyncSession = Depends(get_db)) -> FoodRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: FoodUpdate, session: AsyncSession = Depends(get_db)) -> FoodRead:
        return await super().patch(id, data, session)

    async def create_relation(self, data: FoodCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> FoodRead:
        result = await super().create_relation(data, session)
        return result
