# app/support/superfood/router.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.superfood.model import Superfood
from app.support.superfood.repository import SuperfoodRepository
from app.support.superfood.schemas import (SuperfoodCreate, SuperfoodRead, SuperfoodCreateRelation,
                                           SuperfoodUpdate, SuperfoodCreateResponseSchema)
from app.support.superfood.service import SuperfoodService


class SuperfoodRouter(BaseRouter):  # [SuperfoodCreate, SuperfoodUpdate, SuperfoodRead]):
    def __init__(self):
        super().__init__(
            model=Superfood,
            repo=SuperfoodRepository,
            create_schema=SuperfoodCreate,
            read_schema=SuperfoodRead,
            path_schema=SuperfoodUpdate,
            create_schema_relation=SuperfoodCreateRelation,
            create_response_schema=SuperfoodCreateResponseSchema, prefix="/superfoods",
            tags=["superfoods"],
            service=SuperfoodService
        )

    async def create(self, data: SuperfoodCreate,
                     session: AsyncSession = Depends(get_db)) -> SuperfoodCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int, data: SuperfoodUpdate,
                    session: AsyncSession = Depends(get_db)) -> SuperfoodCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: SuperfoodCreate,
                              session: AsyncSession = Depends(get_db)) -> SuperfoodRead:
        result = await super().create_relation(data, session)
        return result
