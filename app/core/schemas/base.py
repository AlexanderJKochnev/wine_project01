# app/core/schemas/base.py
"""
Базовые Pydantic схемы для валидации данных (включают поля из app/core/models/base_model/Base
# CreateSchema - все поля кроме id и timestamp, обязательныен поля обязательные
# UpdateSchema - все поля кроме id и timestamp, обязательныен поля необязательные
# DeleteResponse -
ReadSchema - все поля кроме tiimestamp
FullSchema - все поля
PaginatedResponse - см ниже на базе ReadSchema
ListResponse - тоже что и Pagianted только без Pagianted
"""
from typing import NewType, Generic, TypeVar, List, Optional, Any
from pydantic import BaseModel, ConfigDict, model_validator
from datetime import datetime

PyModel = NewType("PyModel", BaseModel)
T = TypeVar("T")


class PkSchema(BaseModel):
    """ только счетчик """
    id: int
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class DateSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UniqueSchema(BaseModel):
    """ только уникальные поля """
    name: str


class DescriptionSchema(BaseModel):
    """ добавлять поля описаний на других языках """
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    description_fr: Optional[str] = None


class LangSchema(DescriptionSchema):
    """ добавлять поля на других языках """
    name_ru: Optional[str] = None
    name_fr: Optional[str] = None


class CreateSchema(LangSchema, UniqueSchema):
    """
    остальные поля добавить через CustomCreateSchema
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class UpdateSchema(LangSchema):
    """
    остальные поля добавить через CustomUpdateSchema
    """
    name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class CreateSchemaRelation(LangSchema, UniqueSchema):
    """ схема для создания записей с зависимаостями """
    pass

class ReadSchema(PkSchema, LangSchema, UniqueSchema):
    """
    остальные поля добавить через CustomReadSchema
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class FullSchema(ReadSchema, DateSchema):
    """
    образец - неиспользовать делать DrinkFullSchema(DrinkRead, LangSchema)
    """
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class ReadSchemaWithRealtionships(ReadSchema):
    """ должен возвращаьтб плоские словари есть альтернтива через сервисе """
    model_config = ConfigDict(from_attributes=True,
                              arbitrary_types_allowed=True,
                              extr='allow',
                              populate_by_name=True,
                              exclude_none=True)

    @model_validator(mode='before')
    @classmethod
    def flatten_relationships(cls, data: Any):
        """
            Принимает ORM-объект, возвращает словарь с плоскими значениями (deep levle 2)
            Никакой модификации исходного объекта!
        """
        if hasattr(data, '__dict__') or hasattr(data, '__class__'):
            deep_seep_exclude = tuple(ReadSchema.model_fields.keys())
            deep: dict = {}
            # Это ORM-объект
            result: dict = {}
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
                        # далее при наличи свойства '_sa_instance_state' ищем поля relationships
                        for key, val in value.__dict__.items():
                            if key in deep_seep_exclude:
                                continue
                            if key not in cls.model_fields:
                                continue
                            deep[key] = str(val)
                            # print(f'{field_name}==={key}: {str(val)} {type(val)=}')
                else:
                    result[field_name] = value
            # 4. переопределяем relationships поля
            result.update(deep)
            return result


class ListResponse(BaseModel, Generic[T]):
    """
    просто список instances без пагнинации
    использовать в endpoints - вместо Generic[T] подствлять <model>Read
    """
    items: List[T]
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class PaginatedResponse(BaseModel, Generic[T]):
    """
    использовать в endpoints - вместо Generic[T] подствлять <model>Read
    """
    items: List[T]
    total: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None
    has_next: Optional[int] = None
    has_prev: Optional[int] = None
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)


class DeleteResponse(BaseModel):
    success: bool
    deleted_count: int = 1
    message: str


class ImageMixin:
    image_url: Optional[str] = None  # Добавляем поле для URL изображения
