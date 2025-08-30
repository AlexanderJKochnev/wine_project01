# tests/utility/data_generators.py
from fastapi import FastAPI
from pydantic import BaseModel
import inspect
from typing import Dict, Any, List, get_origin, Union, get_args
import json
from faker import Faker
from decimal import Decimal
# import random

fake = Faker('en-US')


class FieldsData():
    def __init__(self, app: FastAPI, counts: int = 50, percentage: float = 0.5, *args, **kwargs):
        self.exclude_list = ('/auth/token', '/users/')
        self.counts = counts
        self.percenrage = percentage
        self.list_fields_types = self.prepare_test_cases(app, self.exclude_list)
        self.sorted_list = []
        self.outres(self.list_fields_types)  # make self.sorted_list
        # self.prod_list = self.product(self.sorted_list, self.list_fields_types)
        # for n, key in enumerate(self.list_fields_types):
        #    print(f'{n} :: {key}')

    def __call__(self):
        """ результат """
        # return self.topological_sort_with_keys(self.outres(self.list_fields_types))
        # self.print_test_cases()
        return self.product(self.sorted_list, self.list_fields_types)
        # return FakeData(self.prod_list, self.counts, self.percenrage)

    def get_request_models_from_routes(self, app: FastAPI, exclude_list: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Получает модели запросов для POST и PATCH методов из маршрутов FastAPI
        {'/drinks': {'methods': ['POST'],
                     'request_models': {'data': <class 'app.support.drink.schemas.DrinkCreate'>}}}
        """
        route_models = {}

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
                                param.annotation
                            ) and issubclass(param.annotation, BaseModel)):
                                route_models[route_key]['request_models'][param_name] = param.annotation
        return {key: val for key, val in route_models.items() if key not in exclude_list}

    def is_pydantic_model(self, type_hint) -> bool:
        """
        Проверяет, является ли тип Pydantic моделью
        """
        if hasattr(type_hint, 'model_fields'):  # Pydantic v2
            return True
        if hasattr(type_hint, '__fields__'):  # Pydantic v1
            return True
        return False

    def extract_type_from_union(self, union_type) -> tuple:
        """
        Извлекает Pydantic модель илил простые типы данных из Union типа (например, Union[User, None])
        """
        if get_origin(union_type) is Union:
            args = get_args(union_type)
            for arg in args:
                if self.is_pydantic_model(arg):
                    return arg
                # Рекурсивно проверяем вложенные Union
                if get_origin(arg) is Union:
                    nested_model = self.extract_type_from_union(arg)
                    if nested_model:
                        return nested_model
                if arg is not type(None):  # Не NoneType
                    return arg
        return union_type

    def generate_test_data(self, model: BaseModel, required_only: bool = False) -> Dict[str, Any]:
        """
        Генерирует тестовые данные для модели Pydantic
        /drinks = {'methods': ['POST'], 'request_models': {'data': <class 'app.support.drink.schemas.DrinkCreate'>}}
        """
        data = {}
        dependence = []
        fields = model.model_fields  # if hasattr(model, 'model_fields') else model.__fields__
        for field_name, field_info in fields.items():
            # Проверяем обязательность поля
            is_required = (field_info.is_required() if hasattr(field_info, 'is_required') else (
                field_info.required if hasattr(field_info, 'required') else True))
            # Пропускаем необязательные поля если нужна только обязательная информация
            if required_only and not is_required:
                continue
            field_type = field_info.annotation if hasattr(field_info, 'annotation') else field_info.type_
            data[field_name] = self.extract_type_from_union(field_type)
            if field_name.endswith('_id'):
                dependence.append(field_name[0:-3].title())
            continue
        return data, dependence

    def prepare_test_cases(self, app: FastAPI, exclude_list: List[str]) -> List[Dict[str, Any]]:
        """
        Подготавливает списки полей и их типов для всех POST/PATCH маршрутов
        {
        route: /example,
        method: 'POST' | 'PATCH'
        model_name: 'DrinkCreate' (schema name)
        test_data {required_only: {field: value ...},
                   all_fields: {field: value ...}
        }
        """
        route_models = self.get_request_models_from_routes(app, exclude_list)
        test_cases = []

        for route_path, route_info in route_models.items():
            # route_path: /drinks
            # route_info: {'methods': ['POST'], 'request_models':
            # {'data': <class 'app.support.drink.schemas.DrinkCreate'>}
            for method in route_info['methods']:
                request_model = route_info['request_models'].get('data')
                if request_model:
                    # 1. Только обязательные поля
                    required_data, _ = self.generate_test_data(request_model, required_only=True)
                    # 2. Все поля
                    all_data, dependency = self.generate_test_data(request_model, required_only=False)
                    test_case = {'route': route_path, 'method': method, 'model_name': request_model.__name__,
                                 'test_data': {'required_only': required_data, 'all_fields': all_data},
                                 'dependency': dependency}
                    test_cases.append(test_case)
        return test_cases

    def print_test_cases(self):
        """
        Выводит подготовленные тестовые данные
        """
        test_cases = self.list_fields_types

        print(f"Найдено {len(test_cases)} маршрутов для тестирования:\n")

        for i, case in enumerate(test_cases, 1):
            print(f"{i}. {case['method']} {case['route']}")
            print(f"   Модель: {case['model_name']}")
            print("   Обязательные поля:")
            print(f"     {json.dumps(case['test_data']['required_only'], indent=6, ensure_ascii=False)}")
            print("   Все поля:")
            print(f"     {json.dumps(case['test_data']['all_fields'], indent=6, ensure_ascii=False)}")
            print()

    def plural_name(self, name: str) -> str:
        """
        convert name to plural name
        :param namne:
        :type namne:
        :return:
        :rtype:
        """
        if name.endswith('model'):
            name = name[0:-5]
        if not name.endswith('s'):
            if name.endswith('y'):
                name = f'{name[0:-1]}ies'
            else:
                name = f'{name}s'
        return name.title()

    def outres(self, list_fields_types):
        """ создает отсортированный список моделей - очередность заполнения"""
        # {model_name: (model_name1, model_name2, ...)}
        try:
            tmp_dict = {
                key['model_name'].replace('Create', '').replace('Update', ''.replace('Read', '')): key['dependency']
                for key in list_fields_types}
            self.topo_sort(tmp_dict)
        except Exception as e:
            print(f'Ошибка Faker.outres {e}')

    def topo_sort(self, model_dict: dict):
        tier1 = [key for key, val in model_dict.items() if all((not val, key not in self.sorted_list))]
        self.sorted_list.extend(tier1)
        tmp_dict = {key: val for key, val in model_dict.items() if key not in self.sorted_list}
        if tmp_dict:
            for key, val in tmp_dict.items():
                tmp_dict[key] = [a for a in val if a not in self.sorted_list]
            return self.topo_sort(tmp_dict)
        else:
            return None

    def product(self, sorted_list: list, list_fields_types) -> List[Dict[str, Any]]:
        # tmp = sorted(list_fields_types, key=lambda p: p['method'], reverse=True)
        suffix = {'POST': 'Create', 'PATCH': 'Update', 'GET': 'Read'}
        result = []
        for key, val in suffix.items():
            tmp = [b for a in sorted_list for b in list_fields_types
                   if all((b['method'] == key, b['model_name'] == f'{a}{val}'))]
            result.extend(tmp)
        return result


class FakeData():
    def __init__(self, app: FastAPI,
                 # source: List[Dict[str, Any]],
                 counts: int = 50, percentage: float = 0.5, *args, **kwargs):
        """

        :param source: источник данных
        :type source:  FieldsData
        :param counts:  количество генерируемых записей для каждой модели
        :type counts:   int
        :param percentage: соотношение заполненности генериуемых записей полное/минимальное
        :type percentage: float не более  1
        :param args: tbd
        :type args: Any
        :param kwargs: tbd
        :type kwargs: dict
        """
        # отбираем только POST
        source = FieldsData(app)
        self.source: list = [a for a in source() if a['method'] == 'POST']
        # инициация генератора тестовых данных
        self.faker = Faker('en_US')
        # кол-во генерируемых записей - желательно от 20 до 50 что бы протестировать
        # pagination, но не сильно грузить систему
        self.counts = counts
        # какя доля неполных (минимально необходимых данных) будет из общего числа
        self.percentage: float = percentage
        self.dict_res: dict  # словарь генераторов

    def __fake_data__(self, field_name: str, field_type: Any):
        """
        по имени поля и его типу генерирует fake data
        """
        def random_int(min: int = 1, max: int = self.counts):
            return self.faker.random_int(min=min, max=3)

        def fixed_int():
            """ для foreign key для удобства тестировать удаление """
            return 1

        def random_decimal(left_digits: int = 1,
                           right_digits: int = 2,
                           positive: bool = True):
            return self.faker.pyfloat(left_digits=left_digits,
                                      right_digits=right_digits,
                                      positive=positive)

        def random_bool(truth_probability: int = 20):
            return self.faker.pybool(truth_probability=truth_probability)

        if all((field_name.startswith('name'), field_type == str)):
            return self.faker.name
        if all((field_name.startswith('description'), field_type == str)):
            return self.faker.text
        if all((field_name.endswith('_id'), field_type == int)):
            return fixed_int
        if field_type == Decimal:
            return random_decimal
        if field_type == int:
            return random_int
        if field_type == bool:
            return random_bool
        return self.faker.city

    def __single_data_generator__(self, single: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
         создает генератор данных для одной записи одной схемы
        :param single: {route:..., 'test_data': {'required_only': dict(name: type), 'all_fields': ..}
        :type single: dict
        :return: {path: {field_name: value ...}
        :rtype:
        """
        # route = single['route']
        test_data = single['test_data']
        result: dict = {}
        for item in ('required_only', 'all_fields'):
            result[item] = {key: self.__fake_data__(key, val) for key, val in test_data[item].items()}
        return result

    def __data_generator__(self, source: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return {val['route']: self.__single_data_generator__(val) for val in source}

    def __call__(self):
        return self.__data_generator__(self.source)
