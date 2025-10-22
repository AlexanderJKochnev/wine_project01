# app/support/preact/router.py
"""
# handbooks (read only для вываливающихся списков):
    # ! subcategory -> category
    # ! subregion -> region -> country
    # varietals
    # foods -> superfoods
    # superfood
    # sweetness
    # region -> country
    # country
    # category
# create
    # image add
# delete
    # all
# get_all without pagination
# get with pagination
# path all
    # image delete
    # image add
"""


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_active_user_or_internal
from app.core.config.database.db_async import get_db
from app.core.config.project_config import settings
from app.support.subregion.repository import SubregionRepository
from app.support.subregion.service import SubregionService
from app.support.subcategory.repository import SubcategoryRepository
from app.support.subcategory.service import SubcategoryService
from app.support.subregion.model import Subregion
from app.support.region.model import Region
from app.support.country.model import Country


prefix = settings.PREACT_PREFIX

router = APIRouter(prefix=f"/{prefix}", tags=[f"{prefix}"], dependencies=[Depends(get_active_user_or_internal)])
hb_response = dict[int, str]


@router.get("/subregion/en")
async def get_subregion_names_en(session: AsyncSession = Depends(get_db),) -> hb_response:
    repo = SubregionRepository
    service = SubregionService
    return await service.get_english_names(Subregion, Region, Country, repo, session, lang='')


@router.get("/subregion/ru")
async def get_subregion_names_ru(session: AsyncSession = Depends(get_db),) -> hb_response:
    repo = SubregionRepository
    service = SubregionService
    return await service.get_fallback_names(Subregion, Region, Country, repo, session, lang='_ru')


@router.get("/subregion/fr")
async def get_subregion_names_fr(session: AsyncSession = Depends(get_db),) -> hb_response:
    repo = SubregionRepository
    service = SubregionService
    return await service.get_fallback_names(Subregion, Region, Country, repo, session, lang='_fr')


@router.get("/category/en")
async def get_subcategory_names_en(session: AsyncSession = Depends(get_db),) -> hb_response:
    repo = SubcategoryRepository
    service = SubcategoryService
    return await service.get_english_names(repo, session, lang='')


@router.get("/category/ru")
async def get_subcategory_names_ru(session: AsyncSession = Depends(get_db),) -> hb_response:
    repo = SubcategoryRepository
    service = SubcategoryService
    return await service.get_fallback_names(repo, session, lang='_ru')


@router.get("/category/fr")
async def get_subcategory_names_fr(session: AsyncSession = Depends(get_db),) -> hb_response:
    repo = SubcategoryRepository
    service = SubcategoryService
    return await service.get_fallback_names(repo, session, lang='_fr')
