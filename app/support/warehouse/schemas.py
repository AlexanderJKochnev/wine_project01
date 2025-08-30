# app/support/warehouse/schemas.py
from app.core.schemas.base import (CreateSchema, ShortSchema, UpdateSchema,
                                   FullSchema, ReadSchema, ReadSchemaWithRealtionships)
from pydantic import ConfigDict
from typing import Optional


class CustomSchema:
    address: Optional[str] = None
    # customer: Optional[str] = None
    id: int


class CustomCreateSchema:
    address: Optional[str] = None
    customer_id: int  # = Field(..., description="customer ID (Customer.id) для связи Many-to-One")


class CustomUpdSchema:
    address: Optional[str] = None
    customer_id: Optional[int] = None


class WarehouseShort(ShortSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
    login: int


class WarehouseRead(ReadSchemaWithRealtionships):
    # model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              # protected_namespaces=('_',),
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)
    
    customer: Optional[str] = None

class WarehouseCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class WarehouseUpdate(UpdateSchema, CustomUpdSchema):
    pass


class WarehouseFull(FullSchema, CustomSchema):
    pass
