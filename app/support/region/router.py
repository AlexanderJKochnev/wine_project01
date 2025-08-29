# app/support/region/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.region.model import Region
from app.support.region.repository import RegionRepository
from app.support.region.schemas import RegionRead, RegionCreate, RegionUpdate, RegionCreateResponseSchema


class RegionRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Region,
            repo=RegionRepository,
            create_schema=RegionCreate,
            patch_schema=RegionUpdate,
            read_schema=RegionRead,
            prefix="/regions",
            tags=["regions"]
        )
        self.create_response_schema = RegionCreateResponseSchema
        self.setup_routes()

    def setup_routes(self):
        """Настраивает маршруты"""
        self.router.add_api_route("", self.create, methods=["POST"], response_model=self.create_response_schema)
        self.router.add_api_route("", self.get, methods=["GET"], response_model=self.paginated_response)
        self.router.add_api_route("/{id}", self.get_one, methods=["GET"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.patch, methods=["PATCH"], response_model=self.read_schema)
        self.router.add_api_route("/{id}", self.delete, methods=["DELETE"], response_model=self.delete_response)

    async def create(self, data: RegionCreate, session: AsyncSession = Depends(get_db)) -> RegionRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: RegionUpdate,
                    session: AsyncSession = Depends(get_db)) -> RegionRead:
        return await super().patch(id, data, session)


router = RegionRouter().router
