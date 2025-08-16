# app/support/sweetness/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.sweetness.model import Sweetness
from app.support.sweetness.repository import SweetnessRepository
from app.support.sweetness.schemas import SweetnessRead, SweetnessCreate, SweetnessUpdate


class SweetnessRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Sweetness,
            repo=SweetnessRepository,
            create_schema=SweetnessCreate,
            update_schema=SweetnessUpdate,
            read_schema=SweetnessRead,
            prefix="/sweetnesses",
            tags=["sweetnesses"]
        )
        self.setup_routes()

    async def create(self, data: SweetnessCreate, session: AsyncSession = Depends(get_db)) -> SweetnessRead:
        return await super().create(data, session)

    async def update(self, id: int, data: SweetnessUpdate,
                     session: AsyncSession = Depends(get_db)) -> SweetnessRead:
        return await super().update(id, data, session)


router = SweetnessRouter().router
