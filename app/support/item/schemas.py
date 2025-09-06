# app/support/item/schemas.py

from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import BaseModel, DateSchema, FullSchema
from app.support.drink.schemas import DrinkRead
from app.support.warehouse.schemas import WarehouseRead


class CustomReadSchema:
    id: int
    drink: DrinkRead
    warehoise: WarehouseRead
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None
    count: Optional[int] = 0


class CustomCreateSchema:
    drink_id: int
    warehouse_id: int
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None
    count: Optional[int] = 0


class CustomUpdSchema:
    drink_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None
    count: Optional[int] = 0


class CustomFullSchema(CustomReadSchema, DateSchema):
    pass


class ItemRead(BaseModel, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemCreate(BaseModel, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemUpdate(BaseModel, CustomUpdSchema):
    pass


class ItemFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
