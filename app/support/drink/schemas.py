# app/support/drink/schemas.py
# from pydantic import BaseModel, ConfigDict
# from typing import Optional
# from app.core.schemas.base_schema import create_pydantic_models_from_orm
# from app.core.schemas.base_schema import create_detail_view_model
# from app.support.drink.models import Drink
# from app.support.category.models import Category


"""DrinkSchemas = create_pydantic_models_from_orm(Drink)
SAdd = DrinkSchemas['Create']
SUpd = DrinkSchemas['Update']
SDel = DrinkSchemas['DeleteResponse']
SRead = DrinkSchemas['Read']
SList = DrinkSchemas['List']
SDetail = create_detail_view_model(Drink, include_relationships=True)
"""

# class SDetail(BaseModel):
#     model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.support.category.schemas import CategoryBase


class DrinkBase(BaseModel):
    model_config = ConfigDict(rom_attributes=True,
                              arbitrary_types_allowed=True)
    name: str
    name_ru: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    decsription_ru: Optional[str] = None
    category_id: int


class DrinkCreate(DrinkBase):
    model_config = ConfigDict(from_attributes=True)


class DrinkUpdate(DrinkBase):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    name_ru: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    decsription_ru: Optional[str] = None
    category_id: Optional[int] = None


class DrinkRead(DrinkBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryBase
