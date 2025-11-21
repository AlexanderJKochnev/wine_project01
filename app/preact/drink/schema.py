# app/preact/drink/schema.py
"""
    Create
    Delete
    Update
    Get (DetailView)
    GetAll (ListView)
        title
        category + subcategory

"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import Field, model_validator, computed_field
from app.core.utils.common_utils import camel_to_enum
from app.core.schemas.image_mixin import ImageUrlMixin
from app.core.schemas.base import BaseModel, CreateResponse
from app.support.drink.schemas import DrinkCreateRelation, DrinkReadApi, DrinkReadFlat
from app.support.item.model import Item


class ItemListView(BaseModel):
    """
        в поле title попадает значение из sqlalchemy model field
        
    """
    id: int  # Item.id
    vol: Optional[float] = None  # Item.vol
    title: str  # Item.drinks.title or Item.drinks.title_ru or Item.drinks.title_fr
    image_id: Optional[str] = None  # Item.image_id


class ItemDetailView(BaseModel):
    id: int  # Item.id
    vol: Optional[float] = None  # Item.vol
    title: str  # Item.drinks.title or Item.drinks.title_ru or Item.drinks.title_fr
    subtitle: str  # Item.drinks.subtitle or Item.drinks.subtitle_ru or Item.drinks.subtitle_fr
    
    image_id: Optional[str] = None  # Item.image_id