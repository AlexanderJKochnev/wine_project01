# app/support/warehouse/repository.py


from app.support.warehouse.models import Warehouse
from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.orm import selectinload
from sqlalchemy import select


class WarehouseRepository(Repository):
    model = Warehouse

    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Warehouse).options(selectinload(Warehouse.customer))
