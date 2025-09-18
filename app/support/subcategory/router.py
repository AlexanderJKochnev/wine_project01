# app/support/subcategory/auth.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.subcategory.model import Subcategory
from app.support.subcategory.repository import SubcategoryRepository
from app.support.subcategory.schemas import (SubcategoryRead, SubcategoryCreate, SubcategoryUpdate,
                                      SubcategoryCreateRelation, SubcategoryCreateResponseSchema)
from app.support.subcategory.service import SubcategoryService


class SubcategoryRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Subcategory,
            repo=SubcategoryRepository,
            create_schema=SubcategoryCreate,
            read_schema=SubcategoryRead,
            path_schema=SubcategoryUpdate,
            create_schema_relation=SubcategoryCreateRelation,
            create_response_schema=SubcategoryCreateResponseSchema,
            prefix="/subcategories",
            tags=["subcategories"],
            service=SubcategoryService
        )

    async def create(self, data: SubcategoryCreate, session: AsyncSession = Depends(get_db)) -> SubcategoryCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: SubcategoryUpdate, session: AsyncSession = Depends(get_db)) -> SubcategoryCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: SubcategoryCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> SubcategoryRead:
        result = await super().create_relation(data, session)
        return result
