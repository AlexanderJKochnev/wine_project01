# app.support.subcategory.service.py
from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from app.core.utils.common_utils import joiner, dict_sorter
from app.core.services.service import Service
from app.support.category.router import (Category, CategoryRepository, CategoryService)
from app.core.services.service import joint
from app.support.subcategory.model import Subcategory
from app.support.subcategory.schemas import SubcategoryCreateRelation, SubcategoryRead, SubcategoryCreate
from app.support.subcategory.repository import SubcategoryRepository


class SubcategoryService(Service):

    @classmethod
    async def create_relation(cls, data: SubcategoryCreateRelation, repository: SubcategoryRepository,
                              model: Subcategory, session: AsyncSession) -> SubcategoryRead:
        # pydantic model -> dict
        region_data: dict = data.model_dump(exclude={'category'}, exclude_unset=True)
        if data.category:
            result = await CategoryService.get_or_create(data.category, CategoryRepository, Category, session)
            region_data['category_id'] = result.id
        region = SubcategoryCreate(**region_data)
        result = await cls.get_or_create(region, SubcategoryRepository, Subcategory, session)
        return result

    @classmethod
    async def get_english_names(cls, repo, session: AsyncSession,
                                lang: str = '', field_name: str = 'name') -> Dict[int, str]:
        name = f'{field_name}{lang}'
        rows = await repo.fetch_name_triples(category_expr=getattr(Category, name),
                                             subcategory_expr=getattr(Subcategory, name),
                                             session=session)
        result = {row[0]: joiner(joint, row[1], row[2]) for row in rows}
        return dict_sorter(result)

    @classmethod
    async def get_fallback_names(cls, repo, session: AsyncSession,
                                 lang: str = '', field_name: str = 'name') -> Dict[int, str]:
        name = f'{field_name}{lang}'
        rows = await repo.fetch_name_triples(category_expr=func.coalesce(getattr(Category, name),
                                                                         getattr(Category, field_name)),
                                             subcategory_expr=func.coalesce(getattr(Subcategory, name),
                                                                            getattr(Subcategory, field_name)),
                                             session=session)
        result = {row[0]: joiner(joint, row[1], row[2]) for row in rows}
        return dict_sorter(result)
