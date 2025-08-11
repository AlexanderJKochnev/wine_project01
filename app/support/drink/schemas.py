# app/support/drink/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.category.schemas import CategoryShort
from app.support.food.schemas import FoodShort
from pydantic import ConfigDict
from typing import Optional

"""
Custom
Short
Read
Create
Update
Full
"""


class DrinkCustom:
    category_id: int
    food_id: Optional[int]


class DrinkShort(ShortSchema):
    pass


class DrinkRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    category: CategoryShort
    food: FoodShort


class DrinkCreate(BaseSchema, DrinkCustom):
    pass


class DrinkUpdate(UpdateSchema, DrinkCustom):
    pass


class DrinkFull(FullSchema, DrinkCustom):
    pass
