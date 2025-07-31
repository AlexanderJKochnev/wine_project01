# app/support/drink/schemas.py
# import re
# from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field  # field_validator, EmailStr

# from app.core.schemas.notfound import NotFound


class SDrinkAdd(BaseModel):
    title: str = Field(
        ..., description="Name of the drink"
                         )
    subtitle: str = Field(
        ...,
        description="Additional name of the drink")
    category_id: int = Field(
        ..., ge=1, description="Category of the drink")
    description: Optional[str] = Field(
        None, max_length=500,
        description="Description")
    # additional field for foreign key (see service.DrinkDAO(BaseDAO))


class SDrink(SDrinkAdd):
    id: int
    # additional field for foreign key (see service.DrinkDAO(BaseDAO))
    # category: Optional[str] = Field(..., description="Drink category")
