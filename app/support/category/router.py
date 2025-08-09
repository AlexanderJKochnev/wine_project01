# app/support/category/router.py

from app.core.routers.base import BaseRouter
from app.support.category.models import Category
from app.support.category.repository import CategoryRepository
from app.support.category.schemas import CategoryRead
# from app.support.drink.schemas import SUpd

# список подсказок, в дальнейшем загрузить в бд на разных языках и выводить на языке интерфейса
lbl: dict = {'get': 'Список напитков',
             'prefix': 'Напитки',
             'item': 'Напиток',
             'items': 'Напитки',
             'notfound': 'не найден(а)'}


class CategoryRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Category,
            repo=CategoryRepository,
            create_schema=CategoryRead,
            update_schema=CategoryRead,
            read_schema=CategoryRead,
            prefix="/categoriess",
            tags=["categories"]
        )


router = CategoryRouter().router
