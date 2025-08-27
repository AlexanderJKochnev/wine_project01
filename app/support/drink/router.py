# app/support/drink/auth.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.drink.model import Drink
from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import DrinkRead, DrinkCreate, DrinkUpdate, DrinkCreateResponseSchema


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
        self.create_response_schema = DrinkCreateResponseSchema
        self.setup_routes()

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.create_response_schema)
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/{id}", self.get_one, methods=["GET"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.update, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def create(self, data: DrinkCreate, session: AsyncSession = Depends(get_db)) -> DrinkCreateResponseSchema:
        result = await super().create(data, session)
        return result

    async def update(self, id: int, data: DrinkUpdate,
                     session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().update(id, data, session)


router = DrinkRouter().router
