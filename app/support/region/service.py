# app.support.region.service.py
from typing import Type
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.services.service import Service, ModelType, Repository
from app.support.country.router import CountryCreate, Country, CountryRepository, CountryService
from app.support.region.schemas import CreateSchema


class RegionService(Service):
    pass

    async def create_relation(cls, data: ModelType, repository: Type[Repository],
                              model: ModelType, session: AsyncSession) -> ModelType:
        country = {'schema': CountryCreate,
                   'model': Country,
                   'repo': CountryRepository,
                   'service': CountryService}
        create_schema = CreateSchema
        return super().create_relation(data, repository , model, session,
                                       country=country, create_schema=create_schema)