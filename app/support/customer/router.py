# app/support/customer/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.customer.model import Customer
from app.support.customer.schemas import (CustomerRead, CustomerCreate, CustomerUpdate,
                                          CustomerCreateRelation, CustomerCreateResponse)


class CustomerRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Customer,
            prefix="/customers",
        )

    async def create(self, data: CustomerCreate, session: AsyncSession = Depends(get_db)) -> CustomerCreateResponse:
        return await super().create(data, session)

    async def create_relation(self, data: CustomerCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> CustomerCreateResponse:
        return await super().create(data, session)

    async def patch(self, id: int, data: CustomerUpdate,
                    session: AsyncSession = Depends(get_db)) -> CustomerRead:
        return await super().patch(id, data, session)
