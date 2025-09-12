# tests/data_factory/py_factory.py
"""
# Пример с дополнительными настройками
factory_config = {
    "faker_seed": 42,  # Фиксирует случайность для воспроизводимых результатов
    "set_as_default_factory": True,  # Устанавливает фабрику по умолчанию для модели
}

test_data = generate_test_data(User, 3, factory_config)
"""

from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory
from typing import Type, Any, List, Optional, Dict
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID


def generate_test_data(
        model: Type[BaseModel], n: int, factory_kwargs: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
    """
    Генерирует n тестовых данных для указанной Pydantic-модели с использованием Polyfactory.
    Совместимо с Pydantic 2+.

    Args:
        model: Pydantic-модель (возможно с вложенными моделями)
        n: количество генерируемых экземпляров
        factory_kwargs: дополнительные аргументы для кастомизации фабрики

    Returns:
        Список словарей с тестовыми данными
    """
    factory_kwargs = factory_kwargs or {}
    
    # Создаем динамическую фабрику для модели
    factory_class = type(
            f"{model.__name__}Factory", (ModelFactory,), {"__model__": model, **factory_kwargs}
            )
    
    # Генерируем данные
    return [factory_class.build().model_dump() for _ in range(n)]


def generate_test_data_batch(
        model: Type[BaseModel], n: int, factory_kwargs: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
    """
    Генерирует n тестовых данных используя batch-метод для большей производительности.

    Args:
        model: Pydantic-модель
        n: количество генерируемых экземпляров
        factory_kwargs: дополнительные аргументы для кастомизации фабрики

    Returns:
        Список словарей с тестовыми данными
    """
    factory_kwargs = factory_kwargs or {}
    
    # Создаем динамическую фабрику для модели
    factory_class = type(
            f"{model.__name__}Factory", (ModelFactory,), {"__model__": model, **factory_kwargs}
            )
    
    # Генерируем данные батчем
    instances = factory_class.build_batch(n)
    return [instance.model_dump() for instance in instances]


# Пример использования с кастомизацией полей
def generate_custom_test_data(
        model: Type[BaseModel], n: int, field_overrides: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
    """
    Генерирует тестовые данные с кастомными значениями для определенных полей.

    Args:
        model: Pydantic-модель
        n: количество генерируемых экземпляров
        field_overrides: словарь с кастомными значениями или генераторами для полей

    Returns:
        Список словарей с тестовыми данными
    """
    field_overrides = field_overrides or {}
    
    # Создаем фабрику с переопределенными полями
    class CustomFactory(ModelFactory):
        __model__ = model
        
        # Динамически добавляем переопределения полей
        for field_name, value in field_overrides.items():
            if callable(value):
                # Если значение - callable, используем его как метод
                exec(f"@classmethod\ndef {field_name}(cls): return value()")
            else:
                # Иначе используем фиксированное значение
                exec(f"{field_name} = value")
    
    # Генерируем данные
    return [CustomFactory.build().model_dump() for _ in range(n)]


# Пример использования
if __name__ == "__main__":
    class Address(BaseModel):
        street: str
        city: str
        zip_code: str
        country: str = "USA"
    
    
    class User(BaseModel):
        id: UUID
        name: str
        email: str
        age: int
        is_active: bool
        created_at: datetime
        address: Address
        tags: List[str]
        metadata: Dict[str, Any]
    
    
    # Генерируем 3 тестовых набора данных с помощью polyfactory
    print("Сгенерировано с помощью polyfactory:")
    test_data = generate_test_data(User, 3)
    for i, data in enumerate(test_data):
        print(f"{i + 1}: {data}")
    
    # Генерируем батчем (более эффективно)
    print("\nСгенерировано батчем:")
    test_data_batch = generate_test_data_batch(User, 2)
    for i, data in enumerate(test_data_batch):
        print(f"{i + 1}: {data}")
    
    # Генерируем с кастомными значениями
    print("\nСгенерировано с кастомными значениями:")
    custom_fields = {"email": "test@example.com", "age": 25, "is_active": True}
    test_data_custom = generate_custom_test_data(User, 2, custom_fields)
    for i, data in enumerate(test_data_custom):
        print(f"{i + 1}: {data}")
    
    # Генерируем с кастомными генераторами
    print("\nСгенерировано с кастомными генераторами:")
    from faker import Faker
    
    fake = Faker()
    
    custom_generators = {"name": lambda: fake.name(), "email": lambda: fake.email(),
            "created_at": lambda: fake.date_time_this_year()}
    test_data_generators = generate_custom_test_data(User, 2, custom_generators)
    for i, data in enumerate(test_data_generators):
        print(f"{i + 1}: {data}")
