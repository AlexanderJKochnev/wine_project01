# app/support/drink/router.py
from app.core.routers.base import BaseRouter
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import DrinkRead, DrinkCreate, DrinkUpdate


class DrinkRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Drink,
            repo=DrinkRepository,
            create_schema=DrinkCreate,
            update_schema=DrinkUpdate,
            read_schema=DrinkRead,
            prefix="/drinks",
            tags=["drinks"]
        )
        self.setup_routes()

    async def create(self, data: DrinkCreate) -> DrinkRead:
        return await super().create(data)

    async def update(self, id: int, data: DrinkUpdate) -> DrinkRead:
        return await super().update(id, data)


router = DrinkRouter().router
