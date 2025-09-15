# app.support.warehouse.service.py
from app.core.services.service import Service
from app.support.warehouse.router import (Warehouse, AsyncSession, WarehouseRead,
                                          WarehouseCreate, WarehouseCreateRelation, WarehouseRepository)
from app.support.customer.router import Customer, CustomerRepository, CustomerService


class WarehouseService(Service):

    @classmethod
    async def create_relation(cls, data: WarehouseCreateRelation, repository: WarehouseRepository,
                              model: Warehouse, session: AsyncSession) -> WarehouseRead:
        # pydantic model -> dict
        warehouse_data: dict = data.model_dump(exclude={'customer'}, exclude_unset=True)
        if data.customer:
            result = await CustomerService.get_or_create(data.customer, CustomerRepository, Customer, session)
            warehouse_data['customer_id'] = result.id
        warehouse = WarehouseCreate(**warehouse_data)
        result = await WarehouseService.get_or_create(warehouse, WarehouseRepository, Warehouse, session)
        return result
