# app/support/customer/schemas.py

from app.core.schemas.base import BaseSchema, FullSchema, UpdateSchema, ShortSchema
from app.support.category.schemas import CategoryShort
from pydantic import ConfigDict
from typing import Optional


class CustomerCustom:
    firstname: Optional[str]
    lastname: Optional[str]
    account: Optional[str]


class CustomerShort(ShortSchema):
    pass


class CustomerRead(BaseSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)
    category: CategoryShort


class CustomerCreate(BaseSchema, CustomerCustom):
    pass


class CustomerUpdate(UpdateSchema, CustomerCustom):
    pass


class CustomerFull(FullSchema, CustomerCustom):
    pass
