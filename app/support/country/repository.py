# app/support/country/repository.py

from app.support.country.models import Country
from app.core.repositories.sqlalchemy_repository import Repository


class CountryRepository(Repository):
    model = Country
