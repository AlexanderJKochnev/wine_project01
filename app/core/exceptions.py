# app/core/exceptions.py
from typing import Any, Dict, Optional
# from pydantic import BaseModel


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Ошибка валидации данных"""
    pass


class DatabaseException(AppException):
    """Ошибка работы с базой данных"""
    pass


class NotFoundException(AppException):
    """Запись не найдена"""
    pass


class ConflictException(AppException):
    pass
