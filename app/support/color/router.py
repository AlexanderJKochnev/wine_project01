# app/support/color/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.color.model import Color
from app.support.color.repository import ColorRepository
from app.support.color.schemas import (ColorRead, ColorCreate, ColorUpdate,
                                       ColorCreateRelation, ColorCreateResponseSchema)
from app.support.color.service import ColorService


class ColorRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Color,
            repo=ColorRepository,
            create_schema=ColorCreate,
            read_schema=ColorRead,
            create_schema_relation=ColorCreateRelation,
            create_response_schema=ColorCreateResponseSchema,
            prefix="/colors",
            tags=["colors"],
            service=ColorService
        )

    async def create(self, data: ColorCreate, session: AsyncSession = Depends(get_db)) -> ColorCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: ColorUpdate, session: AsyncSession = Depends(get_db)) -> ColorCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: ColorCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> ColorRead:
        result = await super().create_relation(data, session)
        return result
