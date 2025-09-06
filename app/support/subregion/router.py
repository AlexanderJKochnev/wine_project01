# app/support/subregion/router.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.subregion.model import Subregion
from app.support.subregion.repository import SubregionRepository
from app.support.subregion.schemas import SubregionCreate, SubregionRead, SubregionUpdate


class SubregionRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Subregion,
            repo=SubregionRepository,
            create_schema=SubregionCreate,
            patch_schema=SubregionUpdate,
            read_schema=SubregionRead,
            prefix="/subregions",
            tags=["subregions"]
        )
        self.create_response_schema = SubregionRead
        try:
            self.setup_routes()
        except Exception as e:
            print(f'===============subregion routert error {e}==========')

    async def create(self, data: SubregionCreate, session: AsyncSession = Depends(get_db)) -> SubregionRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: SubregionUpdate,
                    session: AsyncSession = Depends(get_db)) -> SubregionRead:
        return await super().patch(id, data, session)


router = SubregionRouter().router
