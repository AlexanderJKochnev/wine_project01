# app/support/color/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_noclass import get_db
from app.core.routers.base import BaseRouter
from app.support.color.models import Color
from app.support.color.repository import ColorRepository
from app.support.color.schemas import ColorRead, ColorCreate, ColorUpdate


class ColorRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Color,
            repo=ColorRepository,
            create_schema=ColorCreate,
            update_schema=ColorUpdate,
            read_schema=ColorRead,
            prefix="/colors",
            tags=["colors"]
        )
        self.setup_routes()

    async def create(self, data: ColorCreate, session: AsyncSession = Depends(get_db)) -> ColorRead:
        return await super().create(data, session)

    async def update(self, id: int, data: ColorUpdate,
                     session: AsyncSession = Depends(get_db)) -> ColorRead:
        return await super().update(id, data, session)


router = ColorRouter().router
