# app/support/region/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.region.model import Region
from app.support.region.repository import RegionRepository
from app.support.region.schemas import RegionRead, RegionCreate, RegionUpdate


class RegionRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Region,
            repo=RegionRepository,
            create_schema=RegionCreate,
            update_schema=RegionUpdate,
            read_schema=RegionRead,
            prefix="/regions",
            tags=["regions"]
        )
        self.setup_routes()

    async def create(self, data: RegionCreate, session: AsyncSession = Depends(get_db)) -> RegionRead:
        return await super().create(data, session)

    async def update(self, id: int, data: RegionUpdate,
                     session: AsyncSession = Depends(get_db)) -> RegionRead:
        return await super().update(id, data, session)


router = RegionRouter().router
