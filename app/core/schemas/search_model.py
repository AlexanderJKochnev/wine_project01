# app/core/models/search_model.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SearchType(str, Enum):
    EXACT = "exact"
    LIKE = "like"


class TextSearchRequest(BaseModel):
    """Модель запроса для текстового поиска"""
    search_fields: Dict[str, str] = Field(
        ...,
        description="Словарь {поле_таблицы: значение_для_поиска}",
        example={"name": "John", "email": "example.com"}
    )
    search_type: SearchType = Field(
        SearchType.EXACT,
        description="Тип поиска: exact - точное совпадение, like - частичное совпадение"
    )
    case_sensitive: bool = Field(
        False,
        description="Чувствительность к регистру (только для exact поиска)"
    )
    limit: Optional[int] = Field(
        None,
        ge=1,
        le=1000,
        description="Ограничение количества записей (1-1000)"
    )
    offset: Optional[int] = Field(
        None,
        ge=0,
        description="Смещение для пагинации"
    )

    class Config:
        schema_extra = {
            "example": {
                "search_fields": {
                    "name": "John",
                    "description": "developer"
                },
                "search_type": "like",
                "case_sensitive": False,
                "limit": 10,
                "offset": 0
            }
        }


class SearchResponse(BaseModel):
    """Модель ответа с результатами поиска"""
    success: bool = Field(..., description="Успешность выполнения запроса")
    data: Optional[List[Dict[str, Any]]] = Field(None, description="Найденные записи")
    total: Optional[int] = Field(None, description="Общее количество найденных записей")
    pagination: Optional[Dict[str, Any]] = Field(None, description="Информация о пагинации")
    message: Optional[str] = Field(None, description="Сообщение о результате")


class ErrorResponse(BaseModel):
    """Модель ответа с ошибкой"""
    success: bool = Field(..., description="Успешность выполнения запроса")
    error: str = Field(..., description="Тип ошибки")
    message: str = Field(..., description="Сообщение об ошибке")
    details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")
    suggestion: Optional[str] = Field(None, description="Предложение по исправлению")
