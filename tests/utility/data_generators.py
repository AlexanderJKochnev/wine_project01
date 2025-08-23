# tests/utility/data_generators.py
from fastapi import FastAPI
from pydantic import BaseModel
import inspect
from typing import Dict, Any, List, Optional
import json


def get_request_models_from_routes(app: FastAPI) -> Dict[str, Dict[str, Any]]:
    """
    Получает модели запросов для POST и PATCH методов из маршрутов FastAPI
    """
    route_models = {}
    exclude_list = ('/auth/token', '/users/')
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = [method for method in route.methods if method in ['POST', 'PATCH']]
            if methods:
                route_key = f"{route.path}"
                route_models[route_key] = {'methods': methods, 'request_models': {}}

                # Ищем модели в зависимостях (для POST/PUT запросов)
                if hasattr(route, 'dependant') and route.dependant:
                    for dependency in route.dependant.dependencies:
                        if hasattr(dependency, 'body_params'):
                            for param in dependency.body_params:
                                if hasattr(param, 'type_') and issubclass(param.type_, BaseModel):
                                    route_models[route_key]['request_models']['body'] = param.type_

                # Альтернативный способ поиска моделей
                if not route_models[route_key]['request_models'] and hasattr(route, 'endpoint'):
                    # Анализируем сигнатуру функции
                    sig = inspect.signature(route.endpoint)
                    for param_name, param in sig.parameters.items():
                        if (param.annotation != inspect.Parameter.empty and inspect.isclass(
                                param.annotation) and issubclass(
                                    param.annotation, BaseModel)):
                            route_models[route_key]['request_models'][param_name] = param.annotation

    return {key: val for key, val in route_models.items() if key not in exclude_list}


def generate_test_data(model: BaseModel, required_only: bool = False) -> Dict[str, Any]:
    """
    Генерирует тестовые данные для модели Pydantic
    """
    data = {}
    fields = model.model_fields  # if hasattr(model, 'model_fields') else model.__fields__

    for field_name, field_info in fields.items():
        # Проверяем обязательность поля
        is_required = (field_info.is_required() if hasattr(field_info, 'is_required') else (
            field_info.required if hasattr(field_info, 'required') else True))
        # Пропускаем необязательные поля если нужна только обязательная информация
        if required_only and not is_required:
            continue

        # Генерируем тестовые значения в зависимости от типа
        field_type = field_info.annotation if hasattr(field_info, 'annotation') else field_info.type_

        if field_type == str:
            data[field_name] = f"test_{field_name}"
        elif field_type == int:
            data[field_name] = 1
        elif field_type == float:
            data[field_name] = 1.0
        elif field_type == bool:
            data[field_name] = True
        elif field_type == list:
            data[field_name] = []
        elif field_type == dict:
            data[field_name] = {}
        else:
            # Для сложных типов пробуем создать экземпляр или используем None
            try:
                if hasattr(field_type, 'model_fields'):
                    data[field_name] = generate_test_data(field_type, required_only)
                else:
                    data[field_name] = field_info
            except Exception:
                data[field_name] = 'some thing else'
        # data[field_name] = field_type
    return data


def prepare_test_cases(app: FastAPI) -> List[Dict[str, Any]]:
    """
    Подготавливает наборы тестовых данных для всех POST/PATCH маршрутов
    """
    route_models = get_request_models_from_routes(app)
    test_cases = []

    for route_path, route_info in route_models.items():
        # route_path: /drinks
        # route_info: {'methods': ['POST'], 'request_models': {'data': <class 'app.support.drink.schemas.DrinkCreate'>}
        for method in route_info['methods']:
            request_model = route_info['request_models'].get('data')
            if request_model:
                # 1. Только обязательные поля
                required_data = generate_test_data(request_model, required_only=True)
                # 2. Все поля
                all_data = generate_test_data(request_model, required_only=False)
                test_case = {'route': route_path,
                             'method': method,
                             'model_name': request_model.__name__,
                             'test_data': {'required_only': required_data, 'all_fields': all_data}}
                test_cases.append(test_case)
    return test_cases


def print_test_cases(app: FastAPI):
    """
    Выводит подготовленные тестовые данные
    """
    test_cases = prepare_test_cases(app)

    print(f"Найдено {len(test_cases)} маршрутов для тестирования:\n")

    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['method']} {case['route']}")
        print(f"   Модель: {case['model_name']}")
        print("   Обязательные поля:")
        print(f"     {json.dumps(case['test_data']['required_only'], indent=6, ensure_ascii=False)}")
        print("   Все поля:")
        print(f"     {json.dumps(case['test_data']['all_fields'], indent=6, ensure_ascii=False)}")
        print()


# Пример использования:
"""
# В вашем тестовом файле:
def test_all_post_patch_routes():
    test_cases = prepare_test_cases(app)

    for case in test_cases:
        route = case['route']
        method = case['method']
        required_data = case['test_data']['required_only']
        all_data = case['test_data']['all_fields']

        # Тест с обязательными полями
        if method == 'POST':
            response = client.post(route, json=required_data)
            assert response.status_code in [200, 201]

        elif method == 'PATCH':
            # Для PATCH обычно нужен ID, адаптируйте под вашу структуру
            response = client.patch(f"{route}/1", json=required_data)
            assert response.status_code == 200

        # Тест со всеми полями
        if method == 'POST':
            response = client.post(route, json=all_data)
            assert response.status_code in [200, 201]
        elif method == 'PATCH':
            response = client.patch(f"{route}/1", json=all_data)
            assert response.status_code == 200
"""


# Вспомогательная функция для более точного определения моделей
def get_body_model_from_endpoint(endpoint_func) -> Optional[BaseModel]:
    """
    Извлекает модель тела запроса из функции эндпоинта
    """
    sig = inspect.signature(endpoint_func)

    for param_name, param in sig.parameters.items():
        if all((param.annotation != inspect.Parameter.empty and inspect.isclass(param.annotation),
                issubclass(param.annotation, BaseModel),
                param_name.lower() in ['body', 'request', 'data'])):
            return param.annotation

    return None
