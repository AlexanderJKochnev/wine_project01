# app/support/category/router.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.category.model import Category
from app.support.category.repository import CategoryRepository
from app.support.category.schemas import CategoryCreate, CategoryRead, CategoryCreateRelation, CategoryUpdate
from app.support.category.service import CategoryService


class CategoryRouter(BaseRouter):  # [CategoryCreate, CategoryUpdate, CategoryRead]):
    def __init__(self):
        super().__init__(
            model=Category,
            repo=CategoryRepository,
            create_schema=CategoryCreate,
            patch_schema=CategoryUpdate,
            read_schema=CategoryRead,
            create_schema_relation=CategoryCreateRelation,
            prefix="/categories",
            tags=["categories"],
            service=CategoryService
        )
        self.setup_routes()

    async def create(self, data: CategoryCreate, session: AsyncSession = Depends(get_db)) -> CategoryRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: CategoryUpdate, session: AsyncSession = Depends(get_db)) -> CategoryRead:
        return await super().patch(id, data, session)

    async def create_relation(self, data: CategoryCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> CategoryRead:
        result = await super().create_relation(data, session)
        return result


router = CategoryRouter().router
