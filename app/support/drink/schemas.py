# app/support/drink/schemas.py
from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.core.schemas.base_schema import create_pydantic_models_from_orm
from app.core.schemas.base_schema import create_detail_view_model
from app.support.drink.models import Drink
from app.support.category.models import Category


DrinkSchemas = create_pydantic_models_from_orm(Drink)
SAdd = DrinkSchemas['Create']
SUpd = DrinkSchemas['Update']
SDel = DrinkSchemas['DeleteResponse']
SRead = DrinkSchemas['Read']
SList = DrinkSchemas['List']
SDetail = create_detail_view_model(Drink, include_relationships=True)


# class SDetail(BaseModel):
#     model_config = ConfigDict(from_attributes=True)
