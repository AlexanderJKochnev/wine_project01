# from pydantic import BaseModel, Field
from app.core.schemas.base_schema import create_pydantic_models_from_orm
from app.support.category.models import Category

CategorySchemas = create_pydantic_models_from_orm(Category)
SAdd = CategorySchemas['Create']
SUpd = CategorySchemas['Update']
SDel = CategorySchemas['DeleteResponse']
SRead = CategorySchemas['Read']
SList = CategorySchemas['List']
