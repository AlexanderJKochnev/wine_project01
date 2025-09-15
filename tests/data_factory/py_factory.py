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
from typing import Type, Any, List, Optional, Dict, Tuple, Union, get_origin, get_args
from decimal import Decimal
import random


def generate_test_data1(
        model: Type[BaseModel], n: int, factory_kwargs: Optional[Dict[str, Any]] = None
        ) -> List[Dict[str, Any]]:
    """
    Генерирует n тестовых данных для указанной Pydantic-модели с использованием Polyfactory.
    Совместимо с Pydantic 2+.

    Args:
        model: Pydantic-модель (возможно с вложенными моделями)
        n: количество генерируемых экземпляров
        factory_kwargs: дополнительные аргументы для кастомизации фабрики
            - faker_seed: int - seed для Faker (для воспроизводимых результатов)
            - set_as_default_factory: bool - установить фабрику как дефолтную для модели
            - providers: Dict[Type, Callable] - кастомные провайдеры для типов данных
            - field_overrides: Dict[str, Any] - переопределения для конкретных полей
            - int_range: Union[Dict[str, Tuple[int, int]], Tuple[int, int]] - диапазоны для целочисленных полей
            - float_range: Union[Dict[str, Tuple[float, float]], Tuple[float, float]] - диапазоны для полей с плавающей точкой
            - decimal_range: Union[Dict[str, Tuple[float, float]], Tuple[float, float]] - диапазоны для Decimal полей

    Returns:
        Список словарей с тестовых данных
    """
    factory_kwargs = factory_kwargs or {}
    
    # Извлекаем настройки диапазонов
    int_range = factory_kwargs.pop('int_range', {})
    float_range = factory_kwargs.pop('float_range', {})
    decimal_range = factory_kwargs.pop('decimal_range', {})
    
    # Обрабатываем глобальные диапазоны (если переданы как кортеж, а не словарь)
    global_int_range = int_range if isinstance(int_range, tuple) else None
    global_float_range = float_range if isinstance(float_range, tuple) else None
    global_decimal_range = decimal_range if isinstance(decimal_range, tuple) else None
    
    # Функция для определения базового типа поля (учитывая Optional и Union)
    def get_base_type(field_type):
        origin = get_origin(field_type)
        if origin is Union or origin is Optional:
            # Для Optional и Union извлекаем не-None типы
            args = [arg for arg in get_args(field_type) if arg is not type(None)]
            return args[0] if args else field_type
        return field_type
    
    # Если переданы глобальные диапазоны, преобразуем их в словари для отдельных полей
    if global_int_range:
        int_range = {}
        for field_name, field_info in model.model_fields.items():
            base_type = get_base_type(field_info.annotation)
            if hasattr(base_type, '__name__') and base_type.__name__ == 'int':
                int_range[field_name] = global_int_range
    
    if global_float_range:
        float_range = {}
        for field_name, field_info in model.model_fields.items():
            base_type = get_base_type(field_info.annotation)
            if hasattr(base_type, '__name__') and base_type.__name__ == 'float':
                float_range[field_name] = global_float_range
    
    if global_decimal_range:
        decimal_range = {}
        for field_name, field_info in model.model_fields.items():
            base_type = get_base_type(field_info.annotation)
            if hasattr(base_type, '__name__') and base_type.__name__ == 'Decimal':
                decimal_range[field_name] = global_decimal_range
    
    # Добавляем обработку Decimal по умолчанию
    default_providers = {Decimal: lambda: Decimal(round(random.uniform(1, 1000), 2))}
    
    # Объединяем с пользовательскими провайдерами
    custom_providers = factory_kwargs.pop('providers', {})
    providers = {**default_providers, **custom_providers}
    
    # Создаем кастомную фабрику
    class CustomFactory(ModelFactory):
        __model__ = model
        
        @classmethod
        def get_provider_map(cls):
            base_providers = super().get_provider_map()
            return {**base_providers, **providers}
    
    # Применяем field_overrides если они есть
    field_overrides = factory_kwargs.pop('field_overrides', {})
    for field_name, value in field_overrides.items():
        setattr(CustomFactory, field_name, value)
    
    # Добавляем обработку диапазонов для полей
    for field_name, (min_val, max_val) in int_range.items():
        setattr(
            CustomFactory, field_name, classmethod(
                    lambda cls, mn=min_val, mx=max_val: random.randint(mn, mx)
                    )
            )
    
    for field_name, (min_val, max_val) in float_range.items():
        setattr(
            CustomFactory, field_name, classmethod(
                    lambda cls, mn=min_val, mx=max_val: random.uniform(mn, mx)
                    )
            )
    
    for field_name, (min_val, max_val) in decimal_range.items():
        setattr(
            CustomFactory, field_name, classmethod(
                    lambda cls, mn=min_val, mx=max_val: Decimal(round(random.uniform(mn, mx), 2))
                    )
            )
    
    # Создаем динамическую фабрику для модели
    factory_class = type(
            f"{model.__name__}Factory", (CustomFactory,), {"__model__": model, **factory_kwargs}
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
    from tests.data_factory.fake_generator import generate_test_data
    from app.support.item.schemas import ItemCreateRelations as schema
    import json
    # Генерируем 3 тестовых набора данных с помощью polyfactory
    print("Сгенерировано с помощью polyfactory:")
    test_number = 3
    test_data = generate_test_data(schema,
                                   test_number,
                                   {'int_range': (1, test_number),
                                    'decimal_range': (0.5, 1),
                                    'float_range': (0.1, 1.0),
                                    # 'field_overrides': {'name': 'Special Product'},
                                    'faker_seed': 42}
    )
    for i, data in enumerate(test_data):
        # print(f"{i + 1}: {data}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
