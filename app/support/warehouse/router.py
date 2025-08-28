# app/support/warehouse/auth.py
"""
    1. Выполни замену Warehouse/warehouse на актуальное имя следующим образом
    1.1. замени warehouses на выбранное имя (мн.число по правилам англ языка в нижнем регистре)
        например для Country это будет ccountries
    1.2. Warehouse -> Country
    1.3. warehouse -> country
    2. Удали эту инструкцию
"""

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.warehouse.model import Warehouse
from app.support.warehouse.repository import WarehouseRepository
from app.support.warehouse.schemas import WarehouseRead, WarehouseCreate, WarehouseUpdate


class WarehouseRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Warehouse,
            repo=WarehouseRepository,
            create_schema=WarehouseCreate,
            patch_schema=WarehouseUpdate,
            read_schema=WarehouseRead,
            prefix="/warehouses",
            tags=["warehouses"]
        )
        self.setup_routes()

    async def create(self, data: WarehouseCreate, session: AsyncSession = Depends(get_db)) -> WarehouseRead:
        return await super().create(data, session)

    async def patch(self, id: int, data: WarehouseUpdate,
                    session: AsyncSession = Depends(get_db)) -> WarehouseRead:
        return await super().patch(id, data, session)


router = WarehouseRouter().router
