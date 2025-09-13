# app/support/item/schemas.py

from decimal import Decimal
from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import BaseModel, CreateResponse, CreateNoNameSchema
from app.support.drink.schemas import DrinkRead, DrinkCreateRelations
from app.support.warehouse.schemas import WarehouseRead, WarehouseCreateRelation


class CustomReadSchema:
    id: int
    drink: DrinkRead
    warehouse: Optional[WarehouseRead] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0


class CustomCreateSchema:
    drink_id: int
    warehouse_id: int
    volume: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0


class CustomCreateRelation:
    drink_id: DrinkCreateRelations
    warehouse_id: WarehouseCreateRelation
    volume: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0


class CustomUpdSchema:
    drink_id: Optional[int] = None
    warehouse_id: Optional[int] = None
    volume: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0


class ItemRead(BaseModel, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemCreate(BaseModel, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemUpdate(BaseModel, CustomUpdSchema):
    pass


class ItemCreateResponseSchema(ItemCreate, CreateResponse):
    pass


class ItemCreateRelationSchema(BaseModel, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
