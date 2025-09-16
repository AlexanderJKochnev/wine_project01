# app/support/drink/schemas.py

# from decimal import Decimal
from typing import List, Optional

from pydantic import ConfigDict

from app.core.schemas.base import (BaseModel, CreateNoNameSchema, CreateResponse, ReadNoNameSchema, UpdateNoNameSchema)
from app.support.category.schemas import CategoryCreateRelation, CategoryRead
from app.support.color.schemas import ColorCreateRelation, ColorRead
from app.support.drink.drink_varietal_schema import DrinkVarietalRelation
from app.support.food.schemas import FoodCreateRelation, FoodRead
# from app.support.item.schemas import ItemRead
from app.support.subregion.schemas import SubregionCreateRelation, SubregionRead
from app.support.sweetness.schemas import SweetnessCreateRelation, SweetnessRead
from app.support.varietal.schemas import VarietalRead
from app.core.schemas.image_mixin import ImageUrlMixin


# from app.support.country.schemas import CountryRead
# from app.support.item.schemas import ItemRead

class CustomCreateRelation:
    image_path: Optional[str] = None
    category: CategoryCreateRelation
    color: Optional[ColorCreateRelation] = None
    sweetness: Optional[SweetnessCreateRelation] = None
    subregion: SubregionCreateRelation
    title: str
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False
    foods: Optional[List[FoodCreateRelation]] = None
    varietals: Optional[List[DrinkVarietalRelation]] = None
    image_path: Optional[str]
    # varietals: List[VarietalCreateRelation]  # item is not fully implemented. circular import  # items: List[ItemRead]


class CustomReadSchema:
    category: Optional[CategoryRead] = None
    color: Optional[ColorRead] = None
    sweetness: Optional[SweetnessRead] = None
    subregion: Optional[SubregionRead] = None
    title: str
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False
    foods: List[FoodRead]
    varietals: List[VarietalRead]


class CustomUpdSchema:
    category: Optional[int] = None
    color: Optional[int] = None
    sweetness: Optional[str] = None
    subregion: Optional[str] = None
    title: Optional[str] = None
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False
    image_path: Optional[str]


class CustomCreateSchema:
    category_id: int
    color_id: Optional[int] = None
    sweetness_id: Optional[int] = None
    subregion_id: int
    title: str
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False
    image_path: Optional[str]
    # description: Optional[str] = None
    # description_fr: Optional[str] = None
    # description_ru: Optional[str] = None


class DrinkRead(ReadNoNameSchema, CustomReadSchema, ImageUrlMixin):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)
    pass


class DrinkCreate(CreateNoNameSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class DrinkCreateRelations(CreateNoNameSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class DrinkUpdate(CustomUpdSchema, UpdateNoNameSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class DrinkCreateResponseSchema(DrinkCreate, CreateResponse):
    pass


class DrinkFoodLinkCreate(BaseModel):
    drink_id: int
    food_ids: List[int]  # полный список ID для связи


class DrinkFoodLinkUpdate(BaseModel):
    food_ids: List[int]


class DrinkVarietalLinkCreate(BaseModel):
    drink_id: int
    varietal_ids: List[int]  # полный список ID для связи


class DrinkVarietalLinkUpdate(BaseModel):
    varietal_ids: List[int]
