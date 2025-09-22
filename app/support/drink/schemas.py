# app/support/drink/schemas.py
from typing import List, Optional

from pydantic import ConfigDict

from app.core.schemas.base import (BaseModel, CreateNoNameSchema, CreateResponse, ReadNoNameSchema, UpdateNoNameSchema)
from app.support.subcategory.schemas import SubcategoryCreateRelation, SubcategoryRead
# from app.support.color.schemas import ColorCreateRelation, ColorRead
from app.support.drink.drink_varietal_schema import DrinkVarietalRelation
from app.support.food.schemas import FoodCreateRelation, FoodRead
from app.support.subregion.schemas import SubregionCreateRelation, SubregionRead
from app.support.sweetness.schemas import SweetnessCreateRelation, SweetnessRead
from app.support.varietal.schemas import VarietalRead
from app.core.schemas.image_mixin import ImageUrlMixin
from app.mongodb.models import ImageCreate, FileResponse


class CustomCreateRelation:
    image_path: Optional[str] = None
    subcategory: SubcategoryCreateRelation
    # color: Optional[ColorCreateRelation] = None
    sweetness: Optional[SweetnessCreateRelation] = None
    subregion: SubregionCreateRelation
    title: str
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_ru: Optional[str] = None
    recommendation_fr: Optional[str] = None
    madeof: Optional[str] = None
    madeof_ru: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    foods: Optional[List[FoodCreateRelation]] = None
    varietals: Optional[List[DrinkVarietalRelation]] = None
    image_path: Optional[str]


class CustomReadSchema:
    subcategory: SubcategoryRead
    # color: Optional[ColorRead] = None
    sweetness: Optional[SweetnessRead] = None
    subregion: Optional[SubregionRead] = None
    title: str
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_ru: Optional[str] = None
    recommendation_fr: Optional[str] = None
    madeof: Optional[str] = None
    madeof_ru: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    foods: List[FoodRead]
    varietals: List[VarietalRead]


class CustomUpdSchema:
    subcategory: Optional[int] = None
    # color: Optional[int] = None
    sweetness: Optional[str] = None
    subregion: Optional[str] = None
    title: Optional[str] = None
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_ru: Optional[str] = None
    recommendation_fr: Optional[str] = None
    madeof: Optional[str] = None
    madeof_ru: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    image_path: Optional[str]


class CustomCreateSchema:
    subcategory_id: int
    # color_id: Optional[int] = None
    sweetness_id: Optional[int] = None
    subregion_id: int
    title: str
    title_native: Optional[str] = None
    subtitle_native: Optional[str] = None
    subtitle: Optional[str] = None
    recommendation: Optional[str] = None
    recommendation_ru: Optional[str] = None
    recommendation_fr: Optional[str] = None
    madeof: Optional[str] = None
    madeof_ru: Optional[str] = None
    alc: Optional[float] = None
    sugar: Optional[float] = None
    aging: Optional[int] = None
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    image_path: Optional[str]
    # description: Optional[str] = None
    # description_fr: Optional[str] = None
    # description_ru: Optional[str] = None


class DrinkRead(ReadNoNameSchema, CustomReadSchema, ImageUrlMixin):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow',
                              populate_by_name=True,
                              exclude_none=True)
    pass


class DrinkCreate(CreateNoNameSchema, CustomCreateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class DrinkCreateRelations(CreateNoNameSchema, CustomCreateRelation):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)


class DrinkCreateRelationsWithImage(DrinkCreateRelations):
    model_config = ConfigDict(from_attributes = True, arbitrary_types_allowed =True, exclude_none = True)
    
    @property
    def image(self) -> Optional[ImageCreate]:
        return Optional[ImageCreate]
    
    

class DrinkUpdate(CustomUpdSchema, UpdateNoNameSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)  # , exclude_none=True)


class DrinkCreateResponseSchema(DrinkCreate, CreateResponse):
    pass


class DrinkFoodLinkCreate(BaseModel):
    drink_id: int
    food_ids: List[int]  # полный список ID для связи


class DrinkFoodLinkUpdate(BaseModel):
    food_ids: List[int]


class DrinkVarietalLinkCreate(BaseModel):
    drink: DrinkRead