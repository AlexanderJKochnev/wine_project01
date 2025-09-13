from pydantic import BaseModel
from polyfactory.factories.pydantic_factory import ModelFactory
from typing import Type, Any, List, Optional, Dict, TypeVar
from datetime import datetime
from uuid import UUID
from faker import Faker

T = TypeVar("T", bound = BaseModel)
fake = Faker()

# Маппинг полей на функции Faker
FAKER_MAPPING = {'name': fake.name, 'email': fake.email, 'first_name': fake.first_name, 'last_name': fake.last_name,
        'address': fake.address, 'city': fake.city, 'country': fake.country, 'zip_code': fake.zipcode,
        'phone': fake.phone_number, 'title': fake.sentence, 'description': fake.text, 'text': fake.text,
        'username': fake.user_name, 'password': fake.password, 'url': fake.url, 'company': fake.company,
        'job': fake.job, 'date': fake.date, 'time': fake.time, 'datetime': fake.date_time,
        'timestamp': lambda: fake.unix_time(), }


def generate_test_data(model: Type[T], n: int) -> List[Dict[str, Any]]:
    """
    Генерирует n тестовых данных для указанной Pydantic-модели с использованием Polyfactory.
    Использует Faker для реалистичных данных.

    Args:
        model: Pydantic-модель (возможно с вложенными моделями)
        n: количество генерируемых экземпляров

    Returns:
        Список словарей с тестовыми данными
    """
    
    # Создаем кастомную фабрику с использованием Faker
    class RealisticFactory(ModelFactory):
        __model__ = model
        
        # Динамически добавляем Faker-генераторы для полей
        for field_name in model.model_fields:
            if field_name in FAKER_MAPPING:
                setattr(
                        RealisticFactory, field_name, classmethod(lambda cls, f=FAKER_MAPPING[field_name]: f())
                        )
    
    # Генерируем данные
    return [RealisticFactory.build().model_dump() for _ in range(n)]


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