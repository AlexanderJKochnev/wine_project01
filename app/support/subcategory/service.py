# app.support.subcategory.service.py
from app.core.services.service import Service
from app.support.category.router import (Category, CategoryRepository, CategoryService)
from app.support.subcategory.router import (AsyncSession, Subcategory, SubcategoryCreate, SubcategoryCreateRelation,
                                            SubcategoryRead, SubcategoryRepository)


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
