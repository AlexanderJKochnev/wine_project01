# app/support/customer/schemas.py

from typing import Optional

from pydantic import ConfigDict
from app.core.schemas.base import DateSchema, BaseModel, PkSchema

# from app.support.warehouse.schemas import WarehouseShort


class CustomReadSchema(PkSchema):
    login: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomCreateSchema(BaseModel):
    login: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomUpdSchema(BaseModel):
    # id: Optional[str]
    login: Optional[str] = None
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    account: Optional[str] = None


class CustomerRead(CustomReadSchema):
    pass


class CustomerCreate(CustomCreateSchema):
    pass


class CustomerUpdate(CustomUpdSchema):
    pass


class CustomerFull(CustomerRead, DateSchema):
    pass


class CustomerCreateResponse(CustomerFull):
    pass


class CustomerCreateRelation(CustomerCreate):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
