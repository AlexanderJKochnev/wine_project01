# from pydantic import BaseModel, Field
# from app.core.schemas.base_schema import create_pydantic_models_from_orm
# from app.support.category.models import Category

# CategorySchemas = create_pydantic_models_from_orm(Category)
# SAdd = CategorySchemas['Create']
# SUpd = CategorySchemas['Update']
# SDel = CategorySchemas['DeleteResponse']
# SRead = CategorySchemas['Read']
# SList = CategorySchemas['List']

from pydantic import ConfigDict
from typing import Optional
from datetime import datetime
from app.core.schemas.base import BaseSchema


class CategoryBase(BaseSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True)
    """ arbitrary_types_allowed=True необходимо если эта схема может быть вложенной """
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
