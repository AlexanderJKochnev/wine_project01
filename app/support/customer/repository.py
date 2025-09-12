# app/support/customer/repository.py

from app.core.repositories.sqlalchemy_repository import Repository
from app.support.customer.model import Customer


class CustomerRepository(Repository):
    model = Customer
