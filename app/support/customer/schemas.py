# app/support/customer/schemas.py

from typing import Optional

from pydantic import ConfigDict
from app.core.schemas.base import DateSchema, BaseModel

# from app.support.warehouse.schemas import WarehouseShort


class CustomReadSchema:
    id: int
    login: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomCreateSchema:
    login: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomUpdSchema:
    login: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomerRead(BaseModel, CustomReadSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CustomerCreate(BaseModel, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CustomerUpdate(BaseModel, CustomUpdSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CustomerFull(CustomerRead, DateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CustomerCreateResponse(CustomerFull):
    pass


class CustomerCreateRelation(CustomerCreate):
    pass