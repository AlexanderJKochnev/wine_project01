# app/support/category/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_noclass import get_db
from app.core.routers.base import BaseRouter
from app.support.category.models import Category
from app.support.category.repository import CategoryRepository
from app.support.category.schemas import CategoryRead, CategoryUpdate, CategoryCreate
# from app.support.drink.schemas import SUpd

# список подсказок, в дальнейшем загрузить в бд на разных языках и выводить на языке интерфейса
lbl: dict = {'get': 'Список напитков',
             'prefix': 'Напитки',
             'item': 'Напиток',
             'items': 'Напитки',
             'notfound': 'не найден(а)'}


class CategoryRouter(BaseRouter[CategoryCreate, CategoryUpdate, CategoryRead]):
    def __init__(self):
        super().__init__(
            model=Category,
            repo=CategoryRepository,
            create_schema=CategoryCreate,
            update_schema=CategoryUpdate,
            read_schema=CategoryRead,
            prefix="/categoriess",
            tags=["categories"]
        )
        self.setup_routes()

        async def create(self, data: CategoryCreate, session: AsyncSession = Depends(get_db)) -> CategoryRead:
            return await super().create(data, session)

        async def update(
                self, id: int, data: CategoryUpdate, session: AsyncSession = Depends(get_db)) -> CategoryRead:
            return await super().update(id, data, session)


router = CategoryRouter().router
