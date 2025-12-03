# app/support/item/schemas.py

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field, model_validator, computed_field
from app.core.utils.common_utils import camel_to_enum
from app.core.schemas.image_mixin import ImageUrlMixin
from app.core.schemas.base import BaseModel, CreateResponse
from app.support.drink.schemas import (DrinkCreateRelation, DrinkReadApi, DrinkReadFlat,
                                       DrinkReadRelation)


class CustomReadFlatSchema:
    id: int
    drink: DrinkReadFlat = Field(exclude=True)
    updated_at: datetime = Field(exclude=True)
    vol: Optional[float] = None
    # price: Optional[float] = None
    # count: Optional[int] = 0

    @computed_field
    @property
    def changed_at(self) -> datetime:
        return getattr(self.drink, "updated_at") or self.updated_at

    @computed_field
    @property
    def country(self) -> str:
        if hasattr(self.drink, 'subregion'):
            if hasattr(self.drink.subregion, 'region'):
                if hasattr(self.drink.subregion.region, 'country'):
                    if hasattr(self.drink.subregion.region.country, 'name'):
                        return camel_to_enum(self.drink.subregion.region.country.name)
        return None

    @computed_field
    @property
    def category(self) -> str:
        if hasattr(self.drink, 'subcategory'):
            if hasattr(self.drink.subcategory, 'category'):
                if hasattr(self.drink.subcategory.category, 'name'):
                    if self.drink.subcategory.category.name == 'Wine':
                        return camel_to_enum(self.drink.subcategory.name)
                    else:
                        return camel_to_enum(self.drink.subcategory.category.name)
        return None

    def _lang_(self, lang: str = 'en') -> Dict[str, Any]:
        return getattr(self.drink, lang)

    @computed_field
    @property
    def en(self) -> Dict[str, Any]:
        return self._lang_('en')

    @computed_field
    @property
    def ru(self) -> Dict[str, Any]:
        return self._lang_('ru')

    @computed_field
    @property
    def fr(self) -> Dict[str, Any]:
        return self._lang_('fr')


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
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class CustomReadRelation:
    drink: DrinkReadRelation
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class CustomCreateRelation:
    drink: DrinkCreateRelation
    # warehouse: Optional[WarehouseCreateRelation] = None
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class DirectUploadSchema(BaseModel):
    total_input: int
    count_of_added_records: int
    error: Optional[list] = None
    error_nmbr: Optional[int] = None


class FileUpload(BaseModel):
    filename: Optional[str] = 'data.json'


class CustomUpdSchema:
    drink_id: Optional[int] = None
    vol: Optional[float] = None
    price: Optional[float] = None
    count: Optional[int] = 0
    image_path: Optional[str] = None
    image_id: Optional[str] = None


class ItemRead(BaseModel, CustomReadFlatSchema, ImageUrlMixin):
    pass


class ItemReadRelation(BaseModel, CustomReadRelation, ImageUrlMixin):
    pass


class ItemReadPreact(ItemRead):
    pass


class ItemCreate(BaseModel, CustomCreateSchema, ImageUrlMixin):
    pass


class ItemUpdate(BaseModel, CustomUpdSchema, ImageUrlMixin):
    pass


class ItemCreateResponseSchema(ItemCreate, CreateResponse):
    pass


class ItemCreateRelation(BaseModel, CustomCreateRelation, ImageUrlMixin):
    pass

# -------------------preact schemas-----------------------


class DrinkPreactDetailView:
    id: int
    drink: DrinkReadApi


class DrinkPreactListView:
    id: int
    drink: int
    vol: Optional[float] = None


class DrinkPreactUpdate:
    id: int


class DrinkPreactCreate:
    title: str
    title_ru: Optional[str]
    title_fr: Optional[str]


class ItemListView(BaseModel):
    # поля не зависят от параметра lang в роуте
    id: int  # Item.id
    vol: Optional[float] = None  # Item.vol
    image_id: Optional[str] = None  # Item.image_id

    title: str  # Item.drinks.title or Item.drinks.title_ru or Item.drinks.title_fr зависит от параметра lang в роуте
    subcategory: str  # Item.drink.subcategoory.category.name + Item.drink.subcategoory.name
    country: str  # Country.name or country.name_ru, or country.name_fr зависит от параметра lang в роуте


class ItemDetailView(BaseModel):
    # поля не зависят от параметра lang в роуте
    id: int  # Item.id
    vol: Optional[float] = None  # Item.vol
    alc: Optional[str] = None
    age: Optional[str] = None
    image_id: Optional[str] = None  # Item.image_id

    # поля зависящие от параметра lang в роуте
    title: str  # Item.drink.title or Item.drinks.title_ru or Item.drinks.title_fr
    subtitle: str
    country: str  # Country.name or country.name_ru, or country.name_fr зависит от параметра lang в роуте
    subcategory: str  # Item.drink.subcategoory.category.name + Item.drink.subcategoory.name
    sweetness: str  # Item.drink.sweetness.name (_ru, _fr)
    recommendation: Optional[str]   # Drink.recommendation (_ru, _fr)
    madeof: Optional[str]   # Drink.madeof (_ru, _fr)
