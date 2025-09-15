# app/support/drink/drink_varietal_schema.py

from typing import List, Optional, Tuple
from pydantic import BaseModel, ConfigDict
from app.support.varietal.router import VarietalCreateRelation


class DrinkVarietalRelation(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)
    varietal: VarietalCreateRelation
    percentage: float
    # varietals: List[Tuple[VarietalCreateRelation, float]]

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
