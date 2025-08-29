# app/core/schemas/base.py
"""
Базовые Pydantic схемы для валидации данных (включают поля из app/core/models/base_model/Base
"""
from typing import NewType, Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime

PyModel = NewType("PyModel", BaseModel)
T = TypeVar("T")


class PkSchema(BaseModel):
    id: int


class UniqueSchema(BaseModel):
    name: str


class ShortSchema(UniqueSchema):
    """
        поля для представления во вложенных схемах
        ...языковой модуль
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class LangSchema(BaseModel):
    """ добавлять поля на других языках """
    name_ru: Optional[str] = None


class DescriptionSchema(BaseModel):
    """ добавлять поля описаний на других языках """
    description: Optional[str] = None
    description_ru: Optional[str] = None


class DateSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReadSchema(ShortSchema, LangSchema, DescriptionSchema, PkSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ReadSchemaWithRealtionships(ReadSchema):
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    @model_validator(mode='before')
    @classmethod
    def flatten_relationships(cls, data: Any):
        """
            Принимает ORM-объект, возвращает словарь с плоскими значениями.
            Никакой модификации исходного объекта!
        """
        if hasattr(data, '__dict__') or hasattr(data, '__class__'):
            # Это ORM-объект
            result = {}
            for field_name in cls.model_fields:
                value = getattr(data, field_name, None)

                # 1. Если это список (many-to-many или many-to-one)
                if isinstance(value, list):
                    # Берём .name у каждого элемента, если есть
                    result[field_name] = [item.name for item in value if
                                          hasattr(item, 'name') and isinstance(getattr(item, 'name'), str)]

                # 2. Если это ORM-объект (одиночное отношение)
                elif hasattr(value, '_sa_instance_state'):  # это ORM-объект
                    if hasattr(value, 'name') and isinstance(value.name, str):
                        result[field_name] = value.name

                    # 3. Вложенные связи: region.country.name
                    elif hasattr(value, 'country') and hasattr(value.country, 'name'):
                        country_name = value.country.name if isinstance(value.country.name, str) else ""
                        if isinstance(value.name, str):
                            result[field_name] = f"{value.name} - {country_name}".strip(" - ")
                        else:
                            result[field_name] = country_name

                    # 4. Другие вложенные шаблоны можно добавить здесь
                    else:
                        result[field_name] = str(value)

                # 5. Простое значение (str, int, bool и т.д.)
                else:
                    result[field_name] = value

            return result


class CreateSchema(UniqueSchema, LangSchema, DescriptionSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UpdateSchema(ShortSchema, LangSchema, DescriptionSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    name: Optional[str] = None


class FullSchema(ReadSchema, DateSchema):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ListResponse(BaseModel, Generic[T]):
    items: List[T]
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_next: Optional[int] = None
    has_prev: Optional[int] = None


class PaginatedResponse(ListResponse[T]):
    pass


class DeleteResponse(BaseModel):
    success: bool
    deleted_count: int = 1
    message: str


class ImageMixin:
    image_url: Optional[str] = None  # Добавляем поле для URL изображения
