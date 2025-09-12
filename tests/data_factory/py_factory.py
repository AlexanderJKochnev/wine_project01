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
from typing import Type, Any, List, Optional, Dict, TypeVar
from datetime import datetime, date, time
from decimal import Decimal
from uuid import UUID

T = TypeVar("T", bound = BaseModel)


def generate_test_data(model: Type[T], n: int) -> List[Dict[str, Any]]:
    """
    Генерирует n тестовых данных для указанной Pydantic-модели с использованием Polyfactory.
    Совместимо с Pydantic 2+.

    Args:
        model: Pydantic-модель (возможно с вложенными моделями)
        n: количество генерируемых экземпляров

    Returns:
        Список словарей с тестовыми данными
    """
    
    # Создаем фабрику для модели
    class DynamicFactory(ModelFactory):
        __model__ = model
    
    # Генерируем данные
    return [DynamicFactory.build().model_dump() for _ in range(n)]


def generate_test_data_batch(model: Type[T], n: int) -> List[Dict[str, Any]]:
    """
    Генерирует n тестовых данных используя batch-метод.

    Args:
        model: Pydantic-модель
        n: количество генерируемых экземпляров

    Returns:
        Список словарей с тестовых данных
    """
    
    # Создаем фабрику для модели
    class DynamicFactory(ModelFactory):
        __model__ = model
    
    # Создаем экземпляр фабрики и используем его build_batch метод
    factory_instance = DynamicFactory()
    instances = factory_instance.build_batch(size = n)
    return [instance.model_dump() for instance in instances]


def generate_custom_test_data(
        model: Type[T], n: int, field_overrides: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
    """
    Генерирует тестовые данные с кастомными значениями для определенных полей.

    Args:
        model: Pydantic-модель
        n: количество генерируемых экземпляров
        field_overrides: словарь с кастомными значениями или генераторами для полей

    Returns:
        Список словарей с тестовых данных
    """
    field_overrides = field_overrides or {}
    
    # Создаем фабрику с переопределенными полями
    class CustomFactory(ModelFactory):
        __model__ = model
        
        # Динамически добавляем переопределения полей
        for field_name, value in field_overrides.items():
            if callable(value):
                # Если значение - callable, создаем свойство
                setattr(CustomFactory, field_name, classmethod(lambda cls, v=value: v()))
            else:
                # Иначе используем фиксированное значение
                setattr(CustomFactory, field_name, value)
    
    # Генерируем данные
    return [CustomFactory.build().model_dump() for _ in range(n)]


def generate_realistic_test_data(
        model: Type[T], n: int, field_mappings: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
    """
    Генерирует более реалистичные тестовые данные с использованием Faker.

    Args:
        model: Pydantic-модель
        n: количество генерируемых экземпляров
        field_mappings: словарь с маппингом имен полей на функции Faker

    Returns:
        Список словарей с тестовых данных
    """
    try:
        from faker import Faker
        fake = Faker()
        
        # Маппинг полей на функции Faker по умолчанию
        default_mappings = {'name': fake.name, 'email': fake.email, 'first_name': fake.first_name,
                'last_name': fake.last_name, 'address': fake.address, 'city': fake.city, 'country': fake.country,
                'zip_code': fake.zipcode, 'phone': fake.phone_number, 'title': fake.sentence, 'description': fake.text,
                'created_at': fake.date_time_this_year, 'updated_at': fake.date_time_this_year, }
        
        # Объединяем с пользовательскими маппингами
        field_mappings = {**default_mappings, **(field_mappings or {})}
        
        # Создаем фабрику с кастомными генераторами
        class RealisticFactory(ModelFactory):
            __model__ = model
            
            # Динамически добавляем кастомные генераторы
            for field_name, generator in field_mappings.items():
                if hasattr(model, 'model_fields') and field_name in model.model_fields:
                    setattr(RealisticFactory, field_name, classmethod(lambda cls, g=generator: g()))
        
        # Генерируем данные
        return [RealisticFactory.build().model_dump() for _ in range(n)]
    
    except ImportError:
        print("Faker не установлен. Используется базовый генератор.")
        return generate_test_data(model, n)


# Альтернативная реализация с использованием create_factory
def generate_test_data_alt(model: Type[T], n: int) -> List[Dict[str, Any]]:
    """
    Альтернативная реализация с использованием ModelFactory.create_factory.
    """
    factory = ModelFactory.create_factory(model)
    instances = factory.build_batch(size = n)
    return [instance.model_dump() for instance in instances]


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
    
    # Генерируем с реалистичными данными
    print("\nСгенерировано с реалистичными данными:")
    test_data_realistic = generate_realistic_test_data(User, 2)
    for i, data in enumerate(test_data_realistic):
        print(f"{i + 1}: {data}")
    
    # Альтернативная реализация
    print("\nСгенерировано альтернативным методом:")
    test_data_alt = generate_test_data_alt(User, 2)
    for i, data in enumerate(test_data_alt):
        print(f"{i + 1}: {data}")
