# app/support/subcategory/router.py

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.subcategory.model import Subcategory
from app.support.subcategory.schemas import (SubcategoryCreate, SubcategoryCreateRelation)


class SubcategoryRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Subcategory,
            prefix="/subcategories",
        )

    async def create(self, data: SubcategoryCreate,
                     session: AsyncSession = Depends(get_db)):
        return await super().create(data, session)

    async def create_relation(self, data: SubcategoryCreateRelation,
                              session: AsyncSession = Depends(get_db)):
        result = await super().create_relation(data, session)
        return result
