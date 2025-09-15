# app/support/warehouse/schemas.py
from typing import Optional

from pydantic import ConfigDict

from app.core.schemas.base import (CreateSchema, FullSchema, ReadSchema,
                                   UpdateSchema, CreateResponse)
from app.support.customer.schemas import CustomerCreate


class CustomCreateRelation:
    customer: CustomerCreate


class CustomReadSchema:
    address: Optional[str] = None
    # customer: Optional[str] = None
    id: int


class CustomCreateSchema:
    address: Optional[str] = None
    customer_id: int  # = Field(..., description="customer ID (Customer.id) для связи Many-to-One")


class CustomUpdSchema:
    address: Optional[str] = None
    customer_id: Optional[int] = None


class WarehouseRead(ReadSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class WarehouseCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class WarehouseCreateRelation(CreateSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class WarehouseUpdate(UpdateSchema, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class WarehouseFull(FullSchema, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class WarehouseCreateResponseSchema(WarehouseCreate, CreateResponse):
    pass
