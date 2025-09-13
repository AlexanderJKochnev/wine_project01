# app/support/drink/router.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.drink.drink_food_repo import DrinkFoodRepository
from app.support.drink.drink_food_service import DrinkFoodService
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import (DrinkCreate, DrinkCreateResponseSchema, DrinkRead,
                                       DrinkUpdate, DrinkFoodLinkUpdate, DrinkCreateRelations)
from app.support.drink.service import DrinkService


class DrinkRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Drink,
            repo=DrinkRepository,
            create_schema=DrinkCreate,
            read_schema=DrinkRead,
            create_schema_relation=DrinkCreateRelations,
            create_response_schema=DrinkCreateResponseSchema,
            prefix="/drinks",
            tags=["drinks"],
            service=DrinkService
        )
        # self.create_response_schema = DrinkCreateResponseSchema

    def setup_routes(self):
        super().setup_routes()
        self.router.add_api_route("/{id}/foods", self.update_drink_foods,
                                  methods=["PATCH"])

    def get_drink_food_service(session: AsyncSession) -> DrinkFoodService:
        repo = DrinkFoodRepository(session)
        return DrinkFoodService(repo)

    async def update_drink_foods(self, id: int,
                                 data: DrinkFoodLinkUpdate,
                                 session: AsyncSession = Depends(get_db)):
        """ обновление many to many """
        service = self.get_drink_food_service(session)
        await service.set_drink_foods(id, data.food_ids)
        return {"status": "success"}

    async def create(self, data: DrinkCreate, session: AsyncSession = Depends(get_db)) -> DrinkCreateResponseSchema:
        result = await super().create(data, session)
        return result

    async def create_relation(self, data: DrinkCreateRelations, session: AsyncSession = Depends(get_db)) -> (
            DrinkCreateResponseSchema):
        result = await super().create_relation(data, session)
        return result

    async def patch(self, id: int, data: DrinkUpdate,
                    session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().patch(id, data, session)
