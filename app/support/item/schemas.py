# app/support/item/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict
from app.support.drink.schemas import ShortSchema as DrinkShort
from app.support.warehouse.schemas import ShortSchema as WarehouseShort
from decimal import Decimal
from typing import Optional


class CustomSchema:
    drink: DrinkShort
    warehoise: WarehouseShort
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None



class CustomCreateSchema:
    drink_id: int
    warehouse_id: int
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None


class CustomUpdSchema:
    drink_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    volume: Optional[Decimal] = None
    price: Optional[Decimal] = None


class ItemShort(ShortSchema):
    pass


class ItemRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemUpdate(UpdateSchema, CustomUpdSchema):
    pass


class ItemFull(FullSchema, CustomSchema):
    pass
