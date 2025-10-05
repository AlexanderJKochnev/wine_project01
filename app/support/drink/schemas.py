# app/support/drink/schemas.py
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import ConfigDict, field_serializer, Field, computed_field

from app.core.schemas.base import (BaseModel, CreateNoNameSchema, CreateResponse, PkSchema,
                                   ReadNoNameSchema, UpdateNoNameSchema, ReadApiSchema)
# from app.core.schemas.image_mixin import ImageUrlMixin
from app.mongodb.models import ImageCreate
# from app.support.color.schemas import ColorCreateRelation, ColorRead
from app.support.drink.drink_varietal_schema import (DrinkVarietalRelation, DrinkVarietalRelationFlat,
                                                     DrinkVarietalRelationApi)
from app.support.drink.drink_food_schema import DrinkFoodRelationApi
from app.support.food.schemas import FoodCreateRelation, FoodRead
from app.support.subcategory.schemas import SubcategoryCreateRelation, SubcategoryRead, SubcategoryReadApiSchema
from app.support.subregion.schemas import SubregionCreateRelation, SubregionRead, SubregionReadApiSchema
from app.support.sweetness.schemas import SweetnessCreateRelation, SweetnessRead
from app.support.varietal.schemas import VarietalRead


class CustomCreateRelation:
    # image_path: Optional[str] = None
    subcategory: SubcategoryCreateRelation
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
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    foods: Optional[List[FoodCreateRelation]] = None
    varietals: Optional[List[DrinkVarietalRelation]] = None


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
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    foods: List[FoodRead]
    varietals: List[VarietalRead]
    varietal_associations: Optional[List[DrinkVarietalRelationFlat]]
    updated_at: Optional[datetime] = None

    @field_serializer('alc', when_used='unless-none')
    def serialize_alc(self, value: Optional[float]) -> Optional[str]:
        if value is None:
            return None
        return f"{int(round(value))}%"

    @field_serializer('sugar', when_used='unless-none')
    def serialize_sugar(self, value: Optional[float]) -> Optional[str]:
        if value is None:
            return None
        return f"{int(round(value))}%"


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
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    # image_path: Optional[str]


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
    age: Optional[str] = None
    sparkling: Optional[bool] = False
    # image_path: Optional[str]
    # description: Optional[str] = None
    # description_fr: Optional[str] = None
    # description_ru: Optional[str] = None


class DrinkRead(ReadNoNameSchema, CustomReadSchema):
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
    """ удлить ?"""
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, exclude_none=True)

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


class CustomReadApiSchema:
    subcategory: SubcategoryReadApiSchema = Field(exclude=True)
    sweetness: Optional[ReadApiSchema] = Field(exclude=True)
    subregion: Optional[SubregionReadApiSchema] = Field(exclude=True)
    title: str = Field(exclude=True)
    title_native: Optional[str] = Field(exclude=True)
    subtitle_native: Optional[str] = Field(exclude=True)
    subtitle: Optional[str] = Field(exclude=True)
    recommendation: Optional[str] = Field(exclude=True)
    recommendation_ru: Optional[str] = Field(exclude=True)
    recommendation_fr: Optional[str] = Field(exclude=True)
    madeof: Optional[str] = Field(exclude=True)
    madeof_ru: Optional[str] = Field(exclude=True)
    alc: Optional[float] = Field(exclude=True)
    sugar: Optional[float] = Field(exclude=True)
    age: Optional[str] = Field(exclude=True)
    sparkling: Optional[bool] = Field(exclude=True)
    foods: Optional[List[FoodRead]] = Field(exclude=True)
    food_associations: Optional[List[DrinkFoodRelationApi]] = Field(exclude=True)
    varietal_associations: Optional[List[DrinkVarietalRelationApi]] = Field(exclude=True)
    updated_at: Optional[datetime] = None
    description: Optional[str] = Field(exclude=True)
    description_ru: Optional[str] = Field(exclude=True)
    description_fr: Optional[str] = Field(exclude=True)

    def __get_field_value__(self, field_name: str, lang_suffix: str) -> Any:
        """Получить значение поля с учетом языкового суффикса"""
        # Пробуем поле с языковым суффиксом
        lang_field = f"{field_name}{lang_suffix}"
        if hasattr(self, lang_field):
            value = getattr(self, lang_field)
            if value is not None:
                return value

        # Если нет поля с суффиксом, пробуем базовое поле
        if hasattr(self, field_name):
            return getattr(self, field_name)

        return None

    def __get_nested_field__(self, obj, field_path: str, lang_suffix: str) -> Any:
        """Получить значение из вложенного объекта"""
        if obj is None:
            return None

        fields = field_path.split('.')
        current_obj = obj

        for field in fields:
            if hasattr(current_obj, field):
                current_obj = getattr(current_obj, field)
            else:
                return None

        # Для вложенных объектов рекурсивно ищем языковые версии
        if hasattr(current_obj, f"name{lang_suffix}"):
            return getattr(current_obj, f"name{lang_suffix}")
        elif hasattr(current_obj, "name"):
            return current_obj.name

        return str(current_obj) if current_obj else None

    def __get_association_names__(self, associations: List, lang_suffix: str) -> str:
        """Получить строку названий ассоциаций"""
        if not associations:
            return ""

        names = []
        for assoc in associations:
            if hasattr(assoc, f"name{lang_suffix}"):
                name = getattr(assoc, f"name{lang_suffix}")
            elif hasattr(assoc, "name"):
                name = assoc.name
            else:
                continue

            if name:
                names.append(name)

        return ", ".join(names) if names else ""

    def __parser__(self, lang_suffix: str) -> Dict[str, Any]:
        """Парсер для преобразования полей в словарь по языкам"""

        # Маппинг суффиксов на названия полей
        lang_map = {"": "en", "_ru": "ru", "_fr": "fr"}
        current_lang = lang_map.get(lang_suffix, "en")

        result = {}

        # Категория и подкатегория
        if self.subcategory:
            # result["category"] = self.__get_nested_field__(self.subcategory, "category.name", lang_suffix)
            # result["subcategory"] = self.__get_nested_field__(self.subcategory, "name", lang_suffix)
            category_name = self.__get_nested_field__(self.subcategory, "category.name", lang_suffix)
            subcategory_name = self.__get_nested_field__(self.subcategory, "name", lang_suffix)
            if category_name and subcategory_name:
                result['category'] = f"{category_name} {subcategory_name}"
            else:
                result['category'] = f"{category_name}"

        # Сладость
        if self.sweetness:
            result["sweetness"] = self.__get_nested_field__(self.sweetness, "name", lang_suffix)

        # Регион и страна
        if self.subregion:
            region_name = self.__get_nested_field__(self.subregion, "name", lang_suffix)
            country_name = self.__get_nested_field__(self.subregion, "region.country.name", lang_suffix)

            if region_name and country_name:
                result["region"] = f"{region_name}, {country_name}"
                result["country"] = country_name
            elif region_name:
                result["region"] = region_name
                result["country"] = self.__get_nested_field__(self.subregion, "region.country.name", lang_suffix)

        # Рекомендации
        result["recommendation"] = self.__get_field_value__("recommendation", lang_suffix)

        # Description
        result["description"] = self.__get_field_value__("description", lang_suffix)

        # Состав
        result["madeof"] = self.__get_field_value__("madeof", lang_suffix)

        # Пайринг (еда)
        result["pairing"] = self.__get_association_names__(self.food_associations, lang_suffix)

        # Сорта винограда
        result["varietals"] = self.__get_association_names__(self.varietal_associations, lang_suffix)

        # Общие поля (одинаковые для всех языков)
        if self.alc is not None:
            result["alc"] = f"{self.alc}%" if current_lang == "en" else f"{self.alc}%"

        if self.sugar is not None:
            result["sugar"] = f"{self.sugar}%" if current_lang == "en" else f"{self.sugar}%"

        result["age"] = self.age
        result["sparkling"] = self.sparkling
        result["title"] = self.title
        result["title_native"] = self.title_native
        result["subtitle_native"] = self.subtitle_native
        result["subtitle"] = self.subtitle

        # Убираем None значения
        return {k: v for k, v in result.items() if v is not None}

    @computed_field
    @property
    def en(self) -> Dict[str, Any]:
        """Английская версия"""
        return self.__parser__("")

    @computed_field
    @property
    def ru(self) -> Dict[str, Any]:
        """Русская версия"""
        return self.__parser__("_ru")

    @computed_field
    @property
    def fr(self) -> Dict[str, Any]:
        """Французская версия"""
        return self.__parser__("_fr")


class DrinkReadApi(PkSchema, CustomReadApiSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extra='allow', populate_by_name=True,
                              exclude_none=True
                              )

    # Эти поля остаются на верхнем уровне
    # updated_at: Optional[datetime] = None
    id: int
