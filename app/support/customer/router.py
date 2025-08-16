# app/support/customer/router.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.customer.model import Customer
from app.support.customer.repository import CustomerRepository
from app.support.customer.schemas import CustomerRead, CustomerCreate, CustomerUpdate


class CustomerRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Customer,
            repo=CustomerRepository,
            create_schema=CustomerCreate,
            update_schema=CustomerUpdate,
            read_schema=CustomerRead,
            prefix="/customers",
            tags=["customers"]
        )
        self.setup_routes()

    async def create(self, data: CustomerCreate, session: AsyncSession = Depends(get_db)) -> CustomerRead:
        return await super().create(data, session)

    async def update(self, id: int, data: CustomerUpdate,
                     session: AsyncSession = Depends(get_db)) -> CustomerRead:
        return await super().update(id, data, session)


router = CustomerRouter().router
