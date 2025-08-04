# from pydantic import BaseModel, Field
from app.core.schemas.base_schema import create_pydantic_models_from_orm
from app.support.category.models import Category


desc_item = "Описание категории напитков"
name_item = "Название категории напитков"
count_item = 'Количество напитков'


"""
        "Create": CreateModel,
        "Update": UpdateModel,
        "Read": ReadModel,
        "DeleteResponse": DeleteResponse
"""
CategorySchemas = create_pydantic_models_from_orm(Category)
SCategoryAdd = CategorySchemas['Create']
SCategoryUpd = CategorySchemas['Update']
SCategoryDel = CategorySchemas['DeleteResponse']
SCategory = CategorySchemas['Read']
SCategoryList = CategorySchemas['List']
# CategoryGet = get_pydantic_model_from_orm(Category, "CategoryGet")

"""
class SCategoryUpd(BaseModel):
    name: str = Field(..., description=name_item)
    description: str = Field(None, description=desc_item)


class SCategory(CategoryGet):
    # id: int
    # count_drink: int = Field(0, description=count_item)
    pass


class SCategoryDel(BaseModel):
    id: int = Field(None)
    name: str = Field(None, description=name_item)
    description: str = Field(None, description=desc_item)
    # count_drink: int = Field(None, description=count_item)
"""
