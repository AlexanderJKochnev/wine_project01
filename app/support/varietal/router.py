# app/support/varietal/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.varietal.model import Varietal
from app.support.varietal.repository import VarietalRepository
from app.support.varietal.schemas import VarietalRead, VarietalCreate, VarietalUpdate, VarietalCreateRelation


class VarietalRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Varietal,
            repo=VarietalRepository,
            create_schema=VarietalCreate,
            patch_schema=VarietalUpdate,
            read_schema=VarietalRead,
            prefix="/varietals",
            tags=["varietals"]
        )
        self.setup_routes()

    async def create(self, data: VarietalCreate, session: AsyncSession = Depends(get_db)) -> VarietalRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: VarietalUpdate,
                     session: AsyncSession = Depends(get_db)) -> VarietalRead:
        return await super().patch(id, data, session)


router = VarietalRouter().router
