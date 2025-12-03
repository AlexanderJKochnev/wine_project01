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
from typing import Optional

from app.core.schemas.base import BaseModel


class ItemListView(BaseModel):
    """
        в поле title попадает значение из sqlalchemy model field
    """
    id: int  # Item.id
    vol: Optional[float] = None  # Item.vol
    title: str  # Item.drinks.title or Item.drinks.title_ru or Item.drinks.title_fr
    subtitle: Optional[str]
    image_id: Optional[str] = None  # Item.image_id


class ItemDetailView(BaseModel):
    id: int  # Item.id
    vol: Optional[float] = None  # Item.vol
    title: str  # Item.drinks.title or Item.drinks.title_ru or Item.drinks.title_fr
    subtitle: str  # Item.drinks.subtitle or Item.drinks.subtitle_ru or Item.drinks.subtitle_fr
    image_id: Optional[str] = None  # Item.image_id


class DrinkListView(BaseModel):
    id: int
    title: str
    # subtitle: Optional[str] = None
    subregion: Optional[str] = None
    subcategory: Optional[str] = None
