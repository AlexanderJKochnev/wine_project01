# app.support.subcategory.service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
from app.support.category.router import (Category, CategoryRepository, CategoryService)
from app.support.subcategory.model import Subcategory
from app.support.subcategory.repository import SubcategoryRepository
from app.support.subcategory.schemas import SubcategoryCreate, SubcategoryCreateRelation, SubcategoryRead


class SubcategoryService(Service):

    @classmethod
    async def create_relation(cls, data: SubcategoryCreateRelation, repository: SubcategoryRepository,
                              model: Subcategory, session: AsyncSession) -> SubcategoryRead:
        # pydantic model -> dict
        category_data: dict = data.model_dump(exclude={'category'}, exclude_unset=True)
        if data.category:
            result = await CategoryService.get_or_create(data.category, CategoryRepository, Category, session)
            category_data['category_id'] = result.id
        region = SubcategoryCreate(**category_data)
        result = await cls.get_or_create(region, SubcategoryRepository, Subcategory, session)
        return result
