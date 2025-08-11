# app/support/customer/repository.py

from app.support.customer.models import Customer
from app.core.repositories.sqlalchemy_repository import Repository
# from sqlalchemy.orm import selectinload
# from sqlalchemy import select
# from app.core.config.database.db_noclass import get_db


# CustomerRepository = RepositoryFactory.get_repository(Customer)
class CustomerRepository(Repository):
    model = Customer


"""
    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Customer).options(selectinload(Customer.category))
"""
