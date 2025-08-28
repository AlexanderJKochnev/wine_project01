# app/support/customer/repository.py

from app.support.customer.model import Customer
from app.core.repositories.sqlalchemy_repository import Repository


# CustomerRepository = RepositoryFactory.get_repository(Customer)
class CustomerRepository(Repository):
    model = Customer


"""
    def get_query(self):
        # Добавляем загрузку связи с relationships
        return select(Customer).options(selectinload(Customer.category))
"""
