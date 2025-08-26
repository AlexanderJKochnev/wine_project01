# tests/utility/schema_validator.py

from typing import Dict, List, Any, Type, Optional, Set
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import Column, inspect
from pydantic import BaseModel
from faker import Faker
from unittest.mock import MagicMock
import re
import inspect
import importlib

fake = Faker()


class TestDataFactory:
    """Фабрика для автоматического создания тестовых данных"""

    @staticmethod
    def create_model_test_data(model: Type[DeclarativeMeta]) -> Dict[str, Any]:
        """Создает тестовые данные для модели"""
        data = {}

        for column in model.__table__.columns:
            if column.primary_key:
                continue

            column_name = column.name
            data[column_name] = TestDataFactory._generate_column_data(column)

        return data

    @staticmethod
    def _generate_column_data(column) -> Any:
        """Генерирует данные на основе типа колонки"""
        column_type = str(column.type)

        if 'VARCHAR' in column_type or 'TEXT' in column_type:
            max_length = 255
            if hasattr(column.type, 'length'):
                max_length = column.type.length
            return fake.text(max_nb_chars=max_length)[:max_length]

        elif 'INTEGER' in column_type:
            return fake.random_int()

        elif 'BOOLEAN' in column_type:
            return fake.boolean()

        elif 'DATETIME' in column_type or 'TIMESTAMP' in column_type:
            return fake.date_time()

        elif 'DATE' in column_type:
            return fake.date()

        elif 'FLOAT' in column_type or 'REAL' in column_type:
            return fake.pyfloat()

        else:
            return fake.word()


class RouteAnalyzer:
    """Анализатор роутеров FastAPI"""

    @staticmethod
    def extract_path_parameters(route_path: str) -> List[str]:
        """Извлекает параметры пути из маршрута"""
        return re.findall(r'\{(\w+)\}', route_path)

    @staticmethod
    def get_route_purpose(route_path: str, methods: Set[str]) -> str:
        """Определяет назначение роута"""
        if 'GET' in methods:
            if '{id}' in route_path or RouteAnalyzer.extract_path_parameters(route_path):
                return 'get_by_id'
            else:
                return 'get_all'
        elif 'POST' in methods:
            return 'create'
        elif 'PUT' in methods or 'PATCH' in methods:
            return 'update'
        elif 'DELETE' in methods:
            return 'delete'
        return 'unknown'

    @staticmethod
    def get_model_from_route(route_path: str) -> Optional[str]:
        """Извлекает имя модели из пути роута"""
        # Убираем параметры пути
        clean_path = re.sub(r'\{.*?\}', '', route_path)
        parts = [p for p in clean_path.split('/') if p and not p.startswith('{')]

        if parts:
            # Берем последнюю часть и преобразуем в CamelCase
            last_part = parts[-1]
            if last_part.endswith('s'):
                last_part = last_part[:-1]  # Убираем множественное число
            return last_part.title().replace('-', '').replace('_', '')
        return None


class SchemaValidator:
    """Валидатор соответствия схем и моделей"""

    @staticmethod
    def validate_schema_model_compatibility(model: Type[DeclarativeMeta], schemas: Dict[str, Type[BaseModel]]):
        """Проверяет соответствие схем и модели"""
        errors = []

        if 'create' in schemas:
            errors.extend(SchemaValidator._validate_create_schema(model, schemas['create']))

        if 'update' in schemas:
            errors.extend(SchemaValidator._validate_update_schema(model, schemas['update']))

        if 'read' in schemas:
            errors.extend(SchemaValidator._validate_read_schema(model, schemas['read']))

        return errors

    @staticmethod
    def _validate_create_schema(model, create_schema):
        errors = []
        model_columns = {col.name for col in model.__table__.columns if not col.primary_key}
        schema_fields = set(create_schema.__annotations__.keys())

        missing_fields = model_columns - schema_fields
        for field in missing_fields:
            errors.append(f"Create schema missing field: {field}")

        extra_fields = schema_fields - model_columns
        for field in extra_fields:
            errors.append(f"Create schema has extra field: {field}")

        return errors

    @staticmethod
    def _validate_update_schema(model, update_schema):
        errors = []
        model_columns = {col.name for col in model.__table__.columns if not col.primary_key}
        schema_fields = set(update_schema.__annotations__.keys())

        missing_fields = model_columns - schema_fields
        for field in missing_fields:
            errors.append(f"Update schema missing field: {field}")

        extra_fields = schema_fields - model_columns
        for field in extra_fields:
            errors.append(f"Update schema has extra field: {field}")

        for field_name, field_type in update_schema.__annotations__.items():
            if not SchemaValidator._is_optional_type(field_type):
                errors.append(f"Update schema field {field_name} should be optional")

        return errors

    @staticmethod
    def _validate_read_schema(model, read_schema):
        errors = []
        model_columns = {col.name for col in model.__table__.columns}
        schema_fields = set(read_schema.__annotations__.keys())

        missing_fields = model_columns - schema_fields
        for field in missing_fields:
            errors.append(f"Read schema missing field: {field}")

        extra_fields = schema_fields - model_columns
        for field in extra_fields:
            errors.append(f"Read schema has extra field: {field}")

        return errors

    @staticmethod
    def _is_optional_type(field_type):
        return (hasattr(field_type, '__origin__') and field_type.__origin__ is Optional)


class TestDataGenerator:
    """Генератор тестовых данных"""

    def __init__(self, mock_database, mock_session):
        self.mock_database = mock_database
        self.mock_session = mock_session
        self.generated_data = {}

    async def generate_data(self, model: Type[DeclarativeMeta], count: int = 10) -> List[Any]:
        """Генерирует тестовые данные для модели"""
        table_name = model.__tablename__

        if table_name not in self.mock_database['tables']:
            self.mock_database['tables'][table_name] = {'data': {}, 'next_id': 1}

        generated_objects = []

        for i in range(count):
            data = TestDataFactory.create_model_test_data(model)
            obj_id = self.mock_database['tables'][table_name]['next_id']
            self.mock_database['tables'][table_name]['next_id'] += 1

            data_with_id = {**data, 'id': obj_id}
            self.mock_database['tables'][table_name]['data'][obj_id] = data_with_id

            mock_obj = MagicMock()
            for key, value in data_with_id.items():
                setattr(mock_obj, key, value)

            generated_objects.append(mock_obj)

        if model.__name__ not in self.generated_data:
            self.generated_data[model.__name__] = []
        self.generated_data[model.__name__].extend(generated_objects)

        return generated_objects


class TestFactory:
    """Фабрика для автоматического создания тестов"""

    @staticmethod
    def create_model_tests(model, schemas):
        """Создает тесты для конкретной модели"""
        tests = []

        # Тест валидации схем
        tests.append(TestFactory._create_schema_validation_test(model, schemas))

        # Тест CRUD операций
        tests.append(TestFactory._create_crud_test(model))

        return tests

    @staticmethod
    def _create_schema_validation_test(model, schemas):
        """Создает тест валидации схем"""

        async def test_schemas():
            errors = SchemaValidator.validate_schema_model_compatibility(model, schemas)
            assert not errors, f"Schema validation errors: {errors}"

        return test_schemas

    @staticmethod
    def _create_crud_test(model):
        """Создает тест CRUD операций"""

        async def test_crud_operations(test_data_generator, mock_async_session):
            # Генерируем тестовые данные
            test_data = TestDataFactory.create_model_test_data(model)

            # Create
            from utility import MockRepository
            repo = MockRepository(model, {'tables': {}})
            created = await repo.create(test_data, mock_async_session)
            assert created is not None

            # Read
            fetched = await repo.get_by_id(created.id, mock_async_session)
            assert fetched is not None

            # Update
            update_data = TestDataFactory.create_model_test_data(model)
            updated = await repo.update(created.id, update_data, mock_async_session)
            assert updated is not None

            # Delete
            deleted = await repo.delete(created.id, mock_async_session)
            assert deleted is True

        return test_crud_operations
