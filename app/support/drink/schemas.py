# app/support/drink/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.category.schemas import CategoryShort
from app.support.food.schemas import FoodShort
from app.support.color.schemas import ColorShort
from app.support.region.schemas import RegionShort
from app.support.sweetness.schemas import SweetnessShort
# from app.support.country.schemas import CountryShort
# from app.support.item.schemas import ItemShort

from pydantic import ConfigDict
from typing import Optional  # , List


class DrinkCustom:
    category_id: int
    region_id: Optional[int]


class DrinkShort(ShortSchema):
    pass


class DrinkRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    category: CategoryShort
    food: Optional[FoodShort]
    color: Optional[ColorShort]
    sweetness: Optional[SweetnessShort]
    region: RegionShort
    # country: CountryShort
    # image_url: Optional[str] = None  # Добавляем поле для URL изображения


class DrinkCreate(BaseSchema, DrinkCustom):
    pass


class DrinkUpdate(UpdateSchema, DrinkCustom):
    pass


class DrinkFull(FullSchema, DrinkCustom):
    pass
