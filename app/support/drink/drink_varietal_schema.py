# app/support/drink/drink_varietal_schema.py
#
from typing import List

from pydantic import BaseModel


class DrinkVarietalLinkCreate(BaseModel):
    drink_id: int
    varietal_ids: List[int]  # полный список ID для связи


class DrinkVarietalLinkUpdate(BaseModel):
    varietal_ids: List[int]


class DrinkDetailResponse(BaseModel):
    """ not used """
    id: int
    name: str
    # ... другие поля ...
    varietals: List[str]  # список __str__() значений

    class Config:
        from_attributes = True
