# app.support.source.router.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.source.model import Source
from app.support.source.schemas import (SourceCreate)
from app.support.source.service import SourceService  # noqa: F401


class SourceRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Source,
            prefix="/source",
        )

    async def create(self, data: SourceCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)
