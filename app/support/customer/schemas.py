# app/support/customer/schemas.py

from app.core.schemas.base import DateSchema
from pydantic import ConfigDict, BaseModel
from typing import Optional
# from app.support.warehouse.schemas import WarehouseShort


class CustomSchema:
    login: str
    firstname: Optional[str]
    lastname: Optional[str]
    account: Optional[str]


class CustomCreateSchema(CustomSchema):
    pass


class CustomUpdSchema:
    login: Optional[str]
    firstname: Optional[str]
    lastname: Optional[str]
    account: Optional[str]


class CustomerShort(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    login: str


class CustomerRead(BaseModel, CustomSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class CustomerCreate(BaseModel, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class CustomerUpdate(BaseModel, CustomUpdSchema):
    pass


# class CustomerFull(BaseModel, DateSchema, CustomSchema):
#     model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
