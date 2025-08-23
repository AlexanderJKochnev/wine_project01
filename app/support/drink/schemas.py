# app/support/drink/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from app.support.category.schemas import CategoryShort
from app.support.food.schemas import FoodShort
from app.support.color.schemas import ColorShort
from app.support.region.schemas import RegionShort
from app.support.sweetness.schemas import SweetnessShort
# from app.support.country.schemas import CountryShort
# from app.support.item.schemas import ItemShort

from pydantic import ConfigDict
from typing import Optional  # , List
from decimal import Decimal


class CustomSchema:
    category: CategoryShort
    food: Optional[FoodShort] = None
    color: Optional[ColorShort] = None
    sweetness: Optional[SweetnessShort] = None
    region: RegionShort
    subtitle: Optional[str] = None
    alcohol: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False


class CustomUpdSchema:
    category_id: Optional[CategoryShort] = None
    food_id: Optional[FoodShort] = None
    color_id: Optional[ColorShort] = None
    sweetness_id: Optional[SweetnessShort] = None
    region_id: Optional[RegionShort] = None
    subtitle: Optional[str] = None
    alcohol: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False


class CustomCreateSchema:
    category_id: int
    food_id: Optional[int] = None
    color_id: Optional[int] = None
    sweetness_id: Optional[int] = None
    region_id: int
    subtitle: Optional[str] = None
    alcohol: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False


class DrinkShort(ShortSchema):
    pass


class DrinkRead(ReadSchema, CustomSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class DrinkCreate(CreateSchema, CustomCreateSchema):
    pass


class DrinkUpdate(UpdateSchema, CustomUpdSchema):
    pass


class DrinkFull(FullSchema, CustomSchema):
    pass
