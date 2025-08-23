# app/support/customer/schemas.py

from app.core.schemas.base import CreateSchema, ReadSchema, ShortSchema, UpdateSchema, FullSchema
from pydantic import ConfigDict
from typing import Optional
from app.support.warehouse.schemas import WarehouseShort


class CustomSchema:
    firstname: Optional[str]
    lastname: Optional[str]
    account: Optional[str]


class CustomCreateSchema:
    pass


class CustomUpdSchema:
    pass


class CustomerShort(ShortSchema):
    pass


class CustomerRead(ReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class CustomerCreate(CreateSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class CustomerUpdate(UpdateSchema, CustomUpdSchema):
    pass


class CustomerFull(FullSchema, CustomSchema):
    pass
