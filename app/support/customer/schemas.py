# app/support/customer/schemas.py

from typing import Optional

from pydantic import BaseModel, ConfigDict


# from app.support.warehouse.schemas import WarehouseShort


class CustomSchema:
    login: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None
    # id: int


class CustomCreateSchema(CustomSchema):
    pass


class CustomUpdSchema:
    login: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomerShort(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    login: str


class CustomerRead(BaseModel, CustomSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CustomerCreate(BaseModel, CustomCreateSchema):  # , CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class CustomerUpdate(BaseModel, CustomUpdSchema):
    pass


# class CustomerFull(BaseModel, DateSchema, CustomSchema):
#     model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
