# app/support/drink/drink_varietal_schema.py
from pydantic import field_serializer, computed_field
from typing import List, Optional
from app.core.schemas.base import BaseModel, ConfigDict
from app.support.varietal.router import VarietalCreateRelation


class DrinkVarietalRelation(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)
    varietal: VarietalCreateRelation
    percentage: Optional[float] = None
    # varietals: List[Tuple[VarietalCreateRelation, float]]


class DrinkVarietalRelationFlat(BaseModel):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)
    varietal: VarietalCreateRelation
    percentage: Optional[float] = None
    
    @computed_field
    @property
    
    
    
    @field_serializer('varietal', when_used = 'unless-none')
    def serialize_varietal(self, value: Optional[dict]) -> Optional[str]:
        if value is None:
            return None
        
        return f"{int(round(value * 100))}%"



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
