# app/support/item/schemas.py

# from decimal import Decimal
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import ConfigDict, Field, model_validator
from app.core.schemas.image_mixin import ImageUrlMixin
from app.core.schemas.base import BaseModel, CreateResponse
from app.support.drink.schemas import DrinkCreateRelations, DrinkReadApi


class CustomReadSchema:
    id: int
    drink: DrinkReadApi = Field(exclude=True)
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0

    # Вычисляемые поля
    updated_at: Optional[datetime] = None
    en: Optional[Dict[str, Any]] = None
    ru: Optional[Dict[str, Any]] = None
    fr: Optional[Dict[str, Any]] = None
    category: Optional[str] = None
    country: Optional[str] = None

    @model_validator(mode='after')
    def extract_drink_data(self) -> 'CustomReadSchema':
        if self.drink:
            self.updated_at = self.drink.updated_at
            self.en = self.drink.en
            self.ru = self.drink.ru
            self.fr = self.drink.fr
            self.category = self.drink.en.get('category')
            self.country = self.drink.en.get('country')
        return self


class CustomCreateSchema:
    drink_id: int
    # warehouse_id: Optional[int]
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class CustomCreateRelation:
    drink: DrinkCreateRelations
    # warehouse: Optional[WarehouseCreateRelation] = None
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class CustomUpdSchema:
    drink_id: Optional[int] = None
    # warehouse_id: Optional[int] = None
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None


class ItemRead(BaseModel, CustomReadSchema, ImageUrlMixin):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemCreate(BaseModel, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class ItemUpdate(BaseModel, CustomUpdSchema):
    pass


class ItemCreateResponseSchema(ItemCreate, CreateResponse):
    pass


class ItemCreateRelations(BaseModel, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)
