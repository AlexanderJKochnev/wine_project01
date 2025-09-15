# app.support.subregion.service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
from app.support.country.router import Country, CountryRepository, CountryService
from app.support.region.router import (Region, RegionCreate, RegionCreateRelation, RegionRead, RegionRepository,
                                       RegionService)
from app.support.subregion.router import (Subregion, SubregionCreate, SubregionRepository)


class SubregionService(Service):

    @classmethod
    async def create_relation(cls, data: RegionCreateRelation, repository: RegionRepository,
                              model: Region, session: AsyncSession) -> RegionRead:
        # pydantic model -> dict
        # subregion_data: dict = data.model_dump(exclude={'country'}, exclude_unset=True)
        if data.region:
            region_data: dict = data.region.model_dump(exclude={'country'}, exclude_unset=True)
            if data.region.country:
                result = await CountryService.get_or_create(data.region.country, CountryRepository, Country, session)
                region_data['country_id'] = result.id
            region = RegionCreate(**region_data)
            result = await RegionService.get_or_create(region, RegionRepository, Region, session)
        subregion_data: dict = data.model_dump(exclude={'region'}, exclude_unset=True)
        subregion_data['region_id'] = result.id
        subregion = SubregionCreate(**subregion_data)
        result = await SubregionService.get_or_create(subregion, SubregionRepository, Subregion, session)
        return result
