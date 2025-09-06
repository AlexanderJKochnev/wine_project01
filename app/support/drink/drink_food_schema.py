# app/support/drink/drink_food_schema.py

from typing import List

from pydantic import BaseModel


class DrinkFoodLinkCreate(BaseModel):
    drink_id: int
    food_ids: List[int]  # полный список ID для связи


class DrinkFoodLinkUpdate(BaseModel):
    food_ids: List[int]


class DrinkDetailResponse(BaseModel):
    id: int
    name: str
    # ... другие поля ...
    foods: List[str]  # список __str__() значений

    class Config:
        from_attributes = True