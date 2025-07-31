from pydantic import BaseModel, Field

desc_item = "Описание категории напитков"
name_item = "Название категории напитков"
count_item = 'Количество напитков'


class SCategoryUpd(BaseModel):
    name: str = Field(..., description=name_item)
    description: str = Field(None, description=desc_item)


class SCategoryAdd(BaseModel):
    name: str = Field(..., description=name_item)
    description: str = Field(None, description=desc_item)
    # count_drink: int = Field(0, description=count_item)


class SCategory(SCategoryAdd):
    id: int
    # count_drink: int = Field(0, description=count_item)


class SCategoryDel(BaseModel):
    id: int = Field(None)
    name: str = Field(None, description=name_item)
    description: str = Field(None, description=desc_item)
    # count_drink: int = Field(None, description=count_item)
