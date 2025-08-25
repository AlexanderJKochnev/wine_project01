# app/support/warehouse/schemas.py
from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict
from typing import Optional


class CustomSchema:
    address: Optional[str] = None


class CustomCreateSchema:
    address: Optional[str] = None
    customer_id: int


class CustomUpdSchema:
    address: Optional[str] = None


class WarehouseShort(ShortSchema):
    pass


class WarehouseRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class WarehouseCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class WarehouseUpdate(UpdateSchema, CustomUpdSchema):
    pass


class WarehouseFull(FullSchema, CustomSchema):
    pass
