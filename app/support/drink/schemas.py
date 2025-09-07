# app/support/drink/schemas.py

from decimal import Decimal
from typing import List, Optional

from pydantic import ConfigDict, Field

from app.core.schemas.base import (CreateSchema, DateSchema, PkSchema, ReadSchemaWithRealtionships,
                                   UpdateSchema, ReadSchema)
from app.support.category.schemas import CategoryRead
from app.support.color.schemas import ColorRead
from app.support.subregion.schemas import SubregionRead
from app.support.sweetness.schemas import SweetnessRead


# from app.support.country.schemas import CountryRead
# from app.support.item.schemas import ItemRead


class CustomReadSchema:
    category_id: Optional[CategoryRead] = None
    # food_id: Optional[FoodRead] = None
    color_id: Optional[ColorRead] = None
    sweetness_id: Optional[SweetnessRead] = None
    subregion_id: Optional[SubregionRead] = None
    subtitle: Optional[str] = None
    alcohol: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False


class CustomCreateSchema:
    category_id: CategoryRead
    # food_id: Optional[FoodRead] = None
    color_id: Optional[ColorRead] = None
    sweetness_id: Optional[SweetnessRead] = None
    subregion_id: Optional[SubregionRead] = None
    subtitle: Optional[str] = None
    alcohol: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False


class CustomUpdSchema:
    category: Optional[int] = None
    color: Optional[int] = None
    sweetness: Optional[str] = None
    subregion: Optional[str] = None
    subtitle: Optional[str] = None
    alcohol: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False


class CustomCreateSchema1:
    category_id: int
    color_id: Optional[int] = None
    sweetness_id: Optional[int] = None
    subregion_id: int
    subtitle: Optional[str] = None
    alcohol: Optional[Decimal] = None
    sugar: Optional[Decimal] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False
    # food: List[str] = []


class DrinkRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)
    pass


class DrinkRead1(ReadSchemaWithRealtionships):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)

    # simple fields
    subtitle: Optional[str] = None
    alcohol: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    sparkling: Optional[bool] = False
    country: Optional[str] = Field(..., json_schema_extra={'parent': 'subregion'},
                                   description='это поле унаследовано от subregion.country'
                                   )  # subregion.country.name
    category: Optional[str] = None
    # relationships field
    color: Optional[str] = None
    sweetness: Optional[str] = None
    subregion: Optional[str] = None
    food: Optional[List[str]] = []


class DrinkCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class DrinkUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class DrinkCreateResponseSchema(DrinkCreate, PkSchema, DateSchema):
    pass
