# app/support/food/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.food.model import Food
from app.support.food.repository import FoodRepository
from app.support.food.schemas import FoodRead, FoodCreate, FoodUpdate


class FoodRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Food,
            repo=FoodRepository,
            create_schema=FoodCreate,
            update_schema=FoodUpdate,
            read_schema=FoodRead,
            prefix="/foods",
            tags=["foods"]
        )
        self.setup_routes()

    async def create(self, data: FoodCreate, session: AsyncSession = Depends(get_db)) -> FoodRead:
        return await super().create(data, session)

    async def update(self, id: int, data: FoodUpdate,
                     session: AsyncSession = Depends(get_db)) -> FoodRead:
        return await super().update(id, data, session)


router = FoodRouter().router
