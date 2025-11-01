# app.support.region.service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
from app.support.country.model import Country
from app.support.country.repository import CountryRepository
from app.support.country.service import CountryService
from app.support.region.model import Region
from app.support.region.schemas import RegionCreate, RegionCreateRelation, RegionRead
from app.support.region.repository import RegionRepository


class RegionService(Service):

    @classmethod
    async def create_relation(cls, data: RegionCreateRelation, repository: RegionRepository,
                              model: Region, session: AsyncSession) -> RegionRead:
        # pydantic model -> dict
        region_data: dict = data.model_dump(exclude={'country'}, exclude_unset=True)
        if data.country:
            result = await CountryService.get_or_create(data.country, CountryRepository, Country, session)
            region_data['country_id'] = result.id
        region = RegionCreate(**region_data)
        result = await cls.get_or_create(region, RegionRepository, Region, session)
        return result
