# app/support/parser/router.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.parser.model import Code, Name, Image, Rawdata
from app.support.subcategory.schemas import (SubcategoryRead, SubcategoryCreate, SubcategoryUpdate,
                                             SubcategoryCreateRelation, SubcategoryCreateResponseSchema)


class CodeRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Code,
            prefix="/codes",
        )

    async def create(self, data: SubcategoryCreate,
                     session: AsyncSession = Depends(get_db)) -> SubcategoryCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: SubcategoryUpdate,
                    session: AsyncSession = Depends(get_db)) -> SubcategoryCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: SubcategoryCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> SubcategoryRead:
        result = await super().create_relation(data, session)
        return result
