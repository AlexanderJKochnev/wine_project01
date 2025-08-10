# app/support/drink/router.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_noclass import get_db
from app.core.routers.base import BaseRouter
from app.support.drink.models import Drink
from app.support.category.models import Category
from app.support.drink.repository import DrinkRepository
from app.support.drink.schemas import DrinkRead, DrinkCreate, DrinkUpdate
from app.core.utils import get_model_fields_info

# список подсказок, в дальнейшем загрузить в бд на разных языках и выводить на языке интерфейса
lbl: dict = {'get': 'Список напитков',
             'prefix': 'Напитки',
             'item': 'Напиток',
             'items': 'Напитки',
             'notfound': 'не найден(а)'}


class DrinkRouter(BaseRouter[DrinkCreate, DrinkUpdate, DrinkRead]):
    def __init__(self):
        super().__init__(
            model=Drink,
            repo=DrinkRepository,
            create_schema=DrinkCreate,
            update_schema=DrinkUpdate,
            read_schema=DrinkRead,
            prefix="/drinks",
            tags=["drinks"]
        )
        self.setup_routes()
        """
        for key, val in get_model_fields_info(Category, 1).items():
            print(f'{key}:: {val}')
        print('---------------create-----------------------')

        for key, val in get_model_fields_info(Category, 2).items():
            print(f'{key}:: {val}')
        print('---------------upate---------------------')

        for key, val in get_model_fields_info(Category, 3).items():
            print(f'{key}:: {val}')
        print('--------------all---------------------')
        for key, val in get_model_fields_info(Category, 0).items():
            print(f'{key}:: {val}')
        print('---------------read-------------------')
        for key, val in get_model_fields_info(Drink, 0).items():
            print(f'{key}:: {val}')
        print('---------------read-------------------')
        """

    async def create(self, data: DrinkCreate, session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().create(data, session)

    async def update(self, id: int, data: DrinkUpdate,
                     session: AsyncSession = Depends(get_db)) -> DrinkRead:
        return await super().update(id, data, session)


router = DrinkRouter().router
