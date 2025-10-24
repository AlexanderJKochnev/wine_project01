# app/core/exceptions.py
from typing import Any, Dict, Optional
# from pydantic import BaseModel


class AppException(Exception):
    """Базовое исключение приложения"""
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        self.message = message
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationException(AppException):
    """Ошибка валидации данных"""
    def __init__(self, detail: Optional[Dict[str, Any]] = None):
        message = "Ошибка валидации данных"
        super().__init__(message, detail)


class DatabaseException(AppException):
    """Ошибка работы с базой данных"""
    def __init__(self, detail: Optional[Dict[str, Any]] = None):
        message = "Ошибка работы с базой данных"
        super().__init__(message, detail)


class NotFoundException(AppException):
    """Запись не найдена"""
    def __init__(self, detail: Optional[Dict[str, Any]] = None):
        message = "Запись не найдена"
        print(f'{message=}=================')
        self.status_code = 404
        super().__init__(message, detail)


class ConflictException(AppException):
    def __init__(self, detail: Optional[Dict[str, Any]] = None):
        message = "Конфликт данных"
        super().__init__(message, detail)
