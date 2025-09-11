# app/support/varietal/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.varietal.model import Varietal
from app.support.varietal.repository import VarietalRepository
from app.support.varietal.schemas import VarietalRead, VarietalCreate, VarietalUpdate, VarietalCreateRelation
from app.support.varietal.service import VarietalService


class VarietalRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Varietal,
            repo=VarietalRepository,
            create_schema=VarietalCreate,
            patch_schema=VarietalUpdate,
            read_schema=VarietalRead,
            prefix="/varietals",
            tags=["varietals"],
            service=VarietalService,
            create_schema_relation=VarietalCreateRelation
        )
        self.setup_routes()

    async def create(self, data: VarietalCreate, session: AsyncSession = Depends(get_db)) -> VarietalRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: VarietalUpdate, session: AsyncSession = Depends(get_db)) -> VarietalRead:
        return await super().patch(id, data, session)

    async def create_relation(self, data: VarietalCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> VarietalRead:
        result = await super().create_relation(data, session)
        return result


router = VarietalRouter().router
