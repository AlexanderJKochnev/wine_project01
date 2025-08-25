# app/support/warehouse/schemas.py
from app.core.schemas.base import CreateSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict, BaseModel, Field
from typing import Optional
from app.support.customer.schemas import CustomerShort


class CustomSchema:
    address: Optional[str] = None
    customer: CustomerShort


class CustomCreateSchema:
    address: Optional[str] = None
    customer_id: int = Field(..., description="customer ID (Customer.id) для связи Many-to-One")


class CustomUpdSchema:
    address: Optional[str] = None


class WarehouseShort(ShortSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    login: int


class WarehouseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class WarehouseCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class WarehouseUpdate(UpdateSchema, CustomUpdSchema):
    pass


class WarehouseFull(FullSchema, CustomSchema):
    pass
