# app/support/country/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.country.model import Country
from app.support.country.repository import CountryRepository
from app.support.country.schemas import CountryRead, CountryCreate, CountryUpdate


class CountryRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Country,
            repo=CountryRepository,
            create_schema=CountryCreate,
            update_schema=CountryUpdate,
            read_schema=CountryRead,
            prefix="/countries",
            tags=["countries"]
        )
        self.setup_routes()

    async def create(self, data: CountryCreate, session: AsyncSession = Depends(get_db)) -> CountryRead:
        return await super().create(data, session)

    async def update(self, id: int, data: CountryUpdate,
                     session: AsyncSession = Depends(get_db)) -> CountryRead:
        return await super().update(id, data, session)


router = CountryRouter().router
