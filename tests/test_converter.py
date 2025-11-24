from copy import deepcopy
from typing import Optional

from pydantic import BaseModel, ValidationError

from app.core.config.project_config import settings
from app.core.utils.common_utils import jprint
from app.core.utils.converters import (drink_level, field_cast, get_subcategory, get_subregion,
                                       read_json_by_keys, get_pairing,
                                       root_level, split_outside_parentheses, string_to_float,
                                       string_to_int, split_outside_parentheses_multi)
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.support.item.schemas import DrinkCreateRelation, ItemCreateRelation  # noqa: F401

filename = 'data.json'


class Item1(BaseModel):
    vol: float
    count: int
    image_path: str


class Country(BaseModel):
    name: str


class Region(BaseModel):
    name: Optional[str] = None
    name_ru: Optional[str] = None
    country: Country


class Subregion(BaseModel):
    name: Optional[str] = None
    name_ru: Optional[str] = None
    region: Region


class Category(BaseModel):
    name: str


class Subcategory(BaseModel):
    name: Optional[str] = None
    name_ru: Optional[str] = None
    category: Category


class Superfoods(BaseModel):
    name: str
    name_ru: Optional[str] = None


class Foods(BaseModel):
    name: str
    name_ru: Optional[str] = None
    superfood: Superfoods


def test_str_to_float():
    x = {'11.23 l': 11.23, '0.34': 0.34, '2,43%': 2.43, '5.00': 5.00,
         'qwe': 0.00
         }
    for a, b in x.items():
        result = string_to_float(a)
        assert result == b, 'ошибка в методе string_to_float {a} != {b}'


def test_str_to_int():
    x = {'11.23 l': 11, '0.34': 0, '2,43%': 2, '5.00': 5,
         'qwe': 0, '3,51': 4, '99.9': 100
         }
    for a, b in x.items():
        result = string_to_int(a)
        assert result == b, f'ошибка в методе string_to_int  {a} != {b}'


def test_casted_fields():
    casted_fields = settings.casted_fields
    test_data = {'vol': '23.4',
                 'count': '21 l',
                 'alc': '123%',
                 'dump': '128763d'}
    expected_data = {'vol': 23.4,
                     'count': 21,
                     'alc': 123.0,
                     'dump': '128763d'}
    for key, val in test_data.items():
        result = field_cast(key, val, casted_fields)
        assert result == expected_data[key]


def test_get_filepath_from_dir_by_name():
    from pathlib import Path
    # 1. получение пути к файлу с данными
    filepath = get_filepath_from_dir_by_name(filename)
    assert isinstance(filepath, Path), f"ошибка получения пути к фалй с данными: {filepath}"


def test_split_outside_parentheses():
    delim = settings.RE_DELIMITER
    test_data = ['Calabria, Villa K.',
                 'Calabria',
                 'Calabria(Seven, Tree ), Palau:',
                 'Palau, Calabria(Seven, Tree).',
                 'Game(venison), Lamb.'
                 ]
    expected = [['Calabria', 'Villa K'],
                ['Calabria', None],
                ['Calabria(Seven, Tree )', 'Palau'],
                ['Palau', 'Calabria(Seven, Tree)'],
                ['Game(venison)', 'Lamb']
                ]
    for n, item in enumerate(test_data):
        result = split_outside_parentheses(item, delim)
        assert result == expected[n]


def test_split_outside_parentheses_multi():
    test_data = ['Calabria, Villa K.',
                 'Calabria',
                 'Calabria(Seven, Tree ), Palau',
                 'Palau, Calabria(Seven, Tree).',
                 'Game(venison), Lamb.',
                 'Game(venison) and Lamb.'
                 ]
    expected = [['Calabria', 'Villa K'],
                ['Calabria'],
                ['Calabria(Seven, Tree )', 'Palau'],
                ['Palau', 'Calabria(Seven, Tree)'],
                ['Game(venison)', 'Lamb'],
                ['Game(venison)', 'Lamb']
                ]
    for n, item in enumerate(test_data):
        result = split_outside_parentheses_multi(item)
        assert result == expected[n], item



def test_read_json_file():
    """ чтение файла с данными """
    filepath = get_filepath_from_dir_by_name(filename)
    #   НАСТРОЙКИ
    # Определяем поля, которые нужно игнорировать ('index', 'isHidden', 'uid', 'imageTimestamp')
    ignored_fields: list = settings.ignored_fields
    # Интернацинальные поля ('vol', 'alc', 'count')
    international_fields = settings.international_fields
    # Конвертируемые поля (остальные поля имеют исходный формат){'vol': 'float', 'count': 'int', 'alc': 'float'}
    casted_fields: dict = settings.casted_fields
    # Поля верхнего уровня (остальные поля в drink ('vol', 'count', 'image_path', 'image_id')
    first_level_fields: list = settings.first_level_fields
    # first_casted: dict = {key: val for key, val in casted_fields.items() if key in first_level_fields}
    # сложные поля ('country', 'category', 'region', 'pairing', 'varietal')
    # complex_fields = settings.complex_fields
    language_key = settings.language_key
    # intl_fields = [val for val in international_fields if val not in first_level_fields]
    delim = settings.RE_DELIMITER

    # TESTS
    for n, (key, value) in enumerate(read_json_by_keys(filepath)):
        # проверка считывания записи из файла
        root_dict: dict = {}
        drink_dict: dict = {}
        assert isinstance(value, dict), "неправльно считана запись из json файла"
        # копирование словаря
        source = deepcopy(value)
        result: dict = root_level(source, first_level_fields, casted_fields)
        # проверка корневого уровня root_level
        try:
            _ = Item1(**result)
            root_dict: dict = result
        except ValidationError as exc:
            jprint(result)
            for error in exc.errors():
                print(f"  Место ошибки (loc): {error['loc']}")
                print(f"  Сообщение (msg): {error['msg']}")
                print(f"  Тип ошибки (type): {error['type']}")
                # input_value обычно присутствует в словаре ошибки
                if 'input_value' in error:
                    print(f"  Некорректное значение (input_value): {error['input_value']}")
                print("-" * 20)
            assert False, 'ошибка в методе: root_level'
        # проверка уровня drink
        result: dict = drink_level(source, casted_fields, language_key)
        drink_dict: dict = result
        # проверка get_subregion
        x = get_subregion(drink_dict, language_key, delim)
        assert x, 'функция get_subregion провалилась'
        assert drink_dict.get('country') is None, 'ключ country не удалился'
        assert drink_dict.get('region') is None, 'ключ region не удалился'
        assert drink_dict.get('region_ru') is None, 'ключ region_ru не удалился'
        try:
            result = drink_dict.get('subregion')
            _ = Subregion(**result)
        except ValidationError as exc:
            jprint(result)
            for error in exc.errors():
                print(f"  Место ошибки (loc): {error['loc']}")
                print(f"  Сообщение (msg): {error['msg']}")
                print(f"  Тип ошибки (type): {error['type']}")
                # input_value обычно присутствует в словаре ошибки
                if 'input_value' in error:
                    print(f"  Некорректное значение (input_value): {error['input_value']}")
                print("-" * 20)
            assert False, 'ошибка в методе: get_subregion'

        # проверка get_subcategory
        x = get_subcategory(drink_dict, language_key, delim)
        assert x, 'функция get_subcategory провалилась'
        assert drink_dict.get('category') is None, 'ключ category не удалился'
        assert drink_dict.get('type') is None, 'ключ type не удалился'
        assert drink_dict.get('type_ru') is None, 'ключ type_ru не удалился'
        try:
            result = drink_dict.get('subcategory')
            _ = Subcategory(**result)
        except ValidationError as exc:
            jprint(result)
            for error in exc.errors():
                print(f"  Место ошибки (loc): {error['loc']}")
                print(f"  Сообщение (msg): {error['msg']}")
                print(f"  Тип ошибки (type): {error['type']}")
                # input_value обычно присутствует в словаре ошибки
                if 'input_value' in error:
                    print(f"  Некорректное значение (input_value): {error['input_value']}")
                print("-" * 20)
            assert False, 'ошибка в методе: get_subcategory'

        # проверка get_pairing
        try:
            # pairing = drink_dict.get('pairing')
            # if pairing:     # pairing is available in data
            x = get_pairing(drink_dict, language_key, delim)
            if not x:
                raise Exception('функция get_pairing провалилась')
            result: list = drink_dict.get('foods')
            if result:
                for item in result:
                    _ = Foods(**item)
        except ValidationError as exc:
            jprint(result)
            for error in exc.errors():
                print(f"  Место ошибки (loc): {error['loc']}")
                print(f"  Сообщение (msg): {error['msg']}")
                print(f"  Тип ошибки (type): {error['type']}")
                # input_value обычно присутствует в словаре ошибки
                if 'input_value' in error:
                    print(f"  Некорректное значение (input_value): {error['input_value']}")
                print("-" * 20)
            assert False, 'ошибка валидации в методе: get_pairing'
        except Exception as e:
            # ====================
            jprint(root_dict)
            print('========')
            for key, val in drink_dict.items():
                print(f'{key}:  {val}')
            # ===================
            assert False, f'ошибка в методе: get_pairing: {e}'
        # assert False
        # if n > 5:
        #     break

