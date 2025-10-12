# app/core/resitories/seacrh_repository.py

# repositories/search_repository.py
from typing import Dict, List, Optional, Type

from sqlalchemy import and_, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.exceptions import DatabaseException, ValidationException
from app.core.schemas.search_model import SearchType


class BaseModel(DeclarativeBase):
    pass


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def text_search(
            self, model: Type[BaseModel], search_fields: Dict[str, str], search_type: SearchType = SearchType.EXACT,
            case_sensitive: bool = False, limit: Optional[int] = None, offset: Optional[int] = None
            ) -> List[BaseModel]:
        """
        Поиск записей по текстовым полям

        Args:
            model: Модель SQLAlchemy для поиска
            search_fields: Словарь {поле: значение} для поиска
            search_type: Тип поиска (exact/like)
            case_sensitive: Чувствительность к регистру
            limit: Ограничение количества записей
            offset: Смещение для пагинации

        Returns:
            List[BaseModel]: Список найденных записей

        Raises:
            ValidationException: Ошибки валидации параметров
            DatabaseException: Ошибки работы с БД
        """
        try:
            # Валидация входных параметров
            await self._validate_search_params(model, search_fields, search_type, limit, offset)
            
            # Построение условий поиска
            conditions = []
            for field_name, search_value in search_fields.items():
                field = getattr(model, field_name)
                condition = self._build_search_condition(
                        field, search_value, search_type, case_sensitive
                        )
                conditions.append(condition)
            
            # Формирование запроса
            query = select(model).where(and_(*conditions))
            
            # Применение пагинации
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            
            # Выполнение запроса
            result = await self.session.execute(query)
            records = result.scalars().all()
            
            return records
        
        except ValidationException:
            raise
        except SQLAlchemyError as e:
            raise DatabaseException(
                    message = "Ошибка при выполнении запроса к базе данных",
                    details = {"error_type": type(e).__name__, "error_details": str(e)},
                    suggestion = "Проверьте корректность параметров запроса и повторите попытку"
                    )
        except Exception as e:
            raise DatabaseException(
                    message = "Неожиданная ошибка при поиске записей",
                    details = {"error_type": type(e).__name__, "error_details": str(e)}
                    )
    
    async def count_text_search(
            self, model: Type[BaseModel], search_fields: Dict[str, str], search_type: SearchType = SearchType.EXACT,
            case_sensitive: bool = False
            ) -> int:
        """Подсчет общего количества записей по условиям поиска"""
        try:
            await self._validate_search_params(model, search_fields, search_type)
            
            conditions = []
            for field_name, search_value in search_fields.items():
                field = getattr(model, field_name)
                condition = self._build_search_condition(
                        field, search_value, search_type, case_sensitive
                        )
                conditions.append(condition)

            query = select(func.count()).select_from(model).where(and_(*conditions))
            result = await self.session.execute(query)
            return result.scalar()

        except SQLAlchemyError as e:
            raise DatabaseException(
                message="Ошибка при подсчете записей", details={"error_details": str(e)}
            )

    def _build_search_condition(self, field, search_value: str, search_type: SearchType, case_sensitive: bool):
        """Построение условия поиска в зависимости от типа"""
        if search_type == SearchType.EXACT:
            if case_sensitive:
                return field == search_value
            else:
                return func.lower(field) == func.lower(search_value)

        elif search_type == SearchType.LIKE:
            if case_sensitive:
                return field.ilike(f"%{search_value}%")
            else:
                return field.ilike(f"%{search_value}%")

        raise ValidationException(
            message=f"Неподдерживаемый тип поиска: {search_type}",
            details={"supported_types": [t.value for t in SearchType]},
            suggestion=f"Используйте один из поддерживаемых типов: {', '.join([t.value for t in SearchType])}"
        )

    async def _validate_search_params(
        self, model: Type[BaseModel], search_fields: Dict[str, str], search_type: SearchType,
        limit: Optional[int] = None, offset: Optional[int] = None
    ):
        """Валидация параметров поиска"""
        errors = []

        # Проверка наличия полей в модели
        for field_name in search_fields.keys():
            if not hasattr(model, field_name):
                errors.append(f"Поле '{field_name}' не существует в модели {model.__name__}")

        # Проверка limit
        if limit is not None and (limit < 1 or limit > 1000):
            errors.append("Лимит должен быть в диапазоне от 1 до 1000")

        # Проверка offset
        if offset is not None and offset < 0:
            errors.append("Смещение не может быть отрицательным")

        # Проверка что переданы поля для поиска
        if not search_fields:
            errors.append("Не указаны поля для поиска")

        if errors:
            raise ValidationException(
                message="Ошибка валидации параметров поиска", details={"validation_errors": errors},
                suggestion="Исправьте указанные ошибки и повторите запрос"
            )
