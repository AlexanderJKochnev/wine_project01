# app/support/drink/schemas.py
# import re
# from datetime import date, datetime
from app.core.schemas.base_schema import create_pydantic_models_from_orm
from app.core.schemas.base_schema import create_detail_view_model
from app.support.drink.models import Drink

DrinkSchemas = create_pydantic_models_from_orm(Drink)
SAdd = DrinkSchemas['Create']
SUpd = DrinkSchemas['Update']
SDel = DrinkSchemas['DeleteResponse']
SRead = DrinkSchemas['Read']
SList = DrinkSchemas['List']
SDetail = create_detail_view_model(Drink, include_relationships=True)