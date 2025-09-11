# app/support/country/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.country.model import Country
from app.support.country.repository import CountryRepository
from app.support.country.schemas import CountryRead, CountryCreate, CountryUpdate, CountryCreateRelation
from app.support.country.service import CountryService


class CountryRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Country,
            repo=CountryRepository,
            create_schema=CountryCreate,
            patch_schema=CountryUpdate,
            read_schema=CountryRead,
            create_schema_relation=CountryCreateRelation,
            prefix="/countries",
            tags=["countries"],
            service=CountryService
        )
        self.setup_routes()

    async def create(self, data: CountryCreate, session: AsyncSession = Depends(get_db)) -> CountryRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: CountryUpdate, session: AsyncSession = Depends(get_db)) -> CountryRead:
        return await super().patch(id, data, session)

    async def create_relation(self, data: CountryCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> CountryRead:
        result = await super().create_relation(data, session)
        return result


router = CountryRouter().router
