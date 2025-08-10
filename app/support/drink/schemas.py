# app/support/drink/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.support.category.schemas import CategoryBase
from app.core.utils import get_model_fields_info  # , get_searchable_fields
from app.support.drink.models import Drink
from app.core.schemas.dynamic_schema import create_drink_schema


class DrinkBase(BaseModel):
    model_config = ConfigDict(from_attributes=True,
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


"""
# DrinkRead = create_drink_schema(Drink, 0)
DrinkCreate = create_drink_schema(Drink, 1,)
DrinkUpdate = create_drink_schema(Drink, 2)
# DrinkRead = create_drink_schema(Drink, 0)


class DrinkRead(BaseModel):
    model_config = ConfigDict(rom_attributes=True,
                              arbitrary_types_allowed=True)
    category: CategoryBase
    name: str
    name_ru: Optional[str] = None
    subtitle: Optional[str] = None
    description: Optional[str] = None
    decsription_ru: Optional[str] = None
    category_id: int

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        ffields = get_model_fields_info(Drink, 0)
        for key, val in ffields.items():
            print(f'{key}: {val}')
"""
