from pydantic import BaseModel, ConfigDict
from typing import Optional
# from app.core.schemas.base_schema import create_pydantic_models_from_orm
# from app.support.category.models import Category

# CategorySchemas = create_pydantic_models_from_orm(Category)
# SAdd = CategorySchemas['Create']
# SUpd = CategorySchemas['Update']
# SDel = CategorySchemas['DeleteResponse']
# SRead = CategorySchemas['Read']
# SList = CategorySchemas['List']

from app.core.schemas.dynamic_schema import create_drink_schema
from app.support.category.models import Category

"""
class CategoryBase(BaseSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True)
    name: str
    name_ru: Optional[str] = None
    count_drink: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
"""

CategoryCreate = create_drink_schema(Category, 1,)
CategoryUpdate = create_drink_schema(Category, 2)
CategoryRead = create_drink_schema(Category, 0, include_list=['count_drink',])


class CategoryBase(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True)
    name: str
    name_ru: Optional[str] = None
    count_drink: int = 0
