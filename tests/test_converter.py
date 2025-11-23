from typing import Optional
from app.core.utils.converters import convert_dict1_to_dict2  # , convert_dict2_to_dict1
from app.core.utils.converters import (convert_custom, batch_convert_data, root_level,
                                       string_to_float, string_to_int, read_json_by_keys,
                                       drink_level, field_cast, split_outside_parentheses,
                                       get_subregion)
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from pydantic import BaseModel, ValidationError, field_validator
from app.core.utils.common_utils import jprint
from app.support.item.schemas import ItemCreateRelation, DrinkCreateRelation  # noqa: F401
from app.core.config.project_config import settings
from copy import deepcopy


filename = 'data.json'


class Item1(BaseModel):
    vol: float
    count: int
    image_path: str


class Country(BaseModel):
    name: str


class Region(BaseModel):
    name: Optional[str]
    name_ru: Optional[str]
    country: Country

class Subregion(BaseModel):
    name: Optional[str]
    name_ru: Optional[str]
    region: Region


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
    test_data = ['Calabria, Villa K',
                 'Calabria',
                 'Calabria(Seven, Tree ), Palau',
                 'Palau, Calabria(Seven, Tree)'
                 ]
    expected = [['Calabria', 'Villa K'],
                ['Calabria', None],
                ['Calabria(Seven, Tree )', 'Palau'],
                ['Palau', 'Calabria(Seven, Tree)']
                ]
    for n, item in enumerate(test_data):
        result = split_outside_parentheses(item, delim)
        assert result == expected[n]


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
    first_casted: dict = {key: val for key, val in casted_fields.items() if key in first_level_fields}
    # сложные поля ('country', 'category', 'region', 'pairing', 'varietal')
    complex_fields = settings.complex_fields
    language_key = settings.language_key
    intl_fields = [val for val in international_fields if val not in first_level_fields]
    delim = settings.RE_DELIMITER
    
    # TESTS
    for n, (key, value) in enumerate(read_json_by_keys(filepath)):
        # проверка считывания записи из файла
        root_dict = {}
        drink_dict = {}
        assert isinstance(value, dict), "неправльно считана запись из json файла"
        # копирование словаря
        source = deepcopy(value)
        result = root_level(source, first_level_fields, casted_fields)
        # проверка корневого уровня root_level
        try:
            _ = Item1(**result)
            root_dict = result
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
        result = drink_level(source, casted_fields, language_key)
        drink_dict = result
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
        # ====================
        jprint(root_dict)
        print('========')
        for key, val in drink_dict.items():
            print(f'{key}:  {val}')
        # ===================
        assert False
        if n > 5:
            break



def test_dict_compair():
    dict1 = {
        "-Lymluc5yKRoLQyYLbJG": {
            "count": 0,
            "vol": 0.75,
            "drink": {
                "alc": 13.5,
                "description": "Intense, concentrated and deep ruby-colored, this wine offers elegant, complex aromas of red fruits. In the mouth it is rich and dense, but harmonious, with sweet, balanced tannins. \nThe wine has a long finish with a depth and structure that ensure its extraordinary longevity.",
                "foods": [
                    {
                        "name": "Game (venison, birds)",
                        "name_ru": "с дичью"
                    },
                    {
                        "name": "Lamb.",
                        "name_ru": "бараниной."
                    }
                ],
                "subregion": {
                    "name": "Bolgheri",
                    "name_ru": "Болгери",
                    "region": {
                        "name": "Tuscany",
                        "name_ru": "Тоскана",
                        "country": {
                            "name": "Italy",
                            "name_ru": None
                        }
                    }
                },
                "subtitle": "Tenuta San Guido",
                "title": "Bolgheri Sassicaia 2014 DOC",
                "varietals": [
                    {
                        "varietal": {
                            "name": "Cabernet Sauvignon 8",
                            "name_ru": "8"
                        },
                        "percentage": 5.0
                    },
                    {
                        "varietal": {
                            "name": "Cabernet Franc 1",
                            "name_ru": "1"
                        },
                        "percentage": 5.0
                    }
                ],
                "description_ru": "Насыщенное, полнотелое вино, глубокого рубинового оттенка предлагает элегантные, сложные ароматы красных фруктов. Вино имеет богатый и плотный, но гармоничный вкус, со сладкими, сбалансированными танинами. \nОбладает послевкусием с глубиной и структурой, обеспечивающей его необычайную продолжительность.",
                "subtitle_ru": "Тенута Сан Гвидо",
                "title_ru": "Болгери Сассициана 2014 DOC",
                "vol_ru": "0.75 l"
            }
        }
    }
    dict2 = {
        "-Lymluc5yKRoLQyYLbJG": {
            "vol": 0.75,
            "drink": {
                "alc": 13.5,
                "description": "Intense, concentrated and deep ruby-colored, this wine offers elegant, complex aromas of red fruits. In the mouth it is rich and dense, but harmonious, with sweet, balanced tannins. The wine has a long finish with a depth and structure that ensure its extraordinary longevity.",
                "subtitle": "Tenuta San Guido",
                "title": "Bolgheri Sassicaia 2014 DOC",
                "description_ru": "Насыщенное, полнотелое вино, глубокого рубинового оттенка предлагает элегантные, сложные ароматы красных фруктов. Вино имеет богатый и плотный, но гармоничный вкус, со сладкими, сбалансированными танинами. Обладает послевкусием с глубиной и структурой, обеспечивающей его необычайную продолжительность.",
                "subtitle_ru": "Тенута Сан Гвидо",
                "title_ru": "Болгери Сассициана 2014 DOC",
                "subregion": {
                    "name": "Bolgheri",
                    "name_ru": "Болгери",
                    "region": {
                        "name": "Tuscany",
                        "name_ru": "Тоскана",
                        "country": {
                            "name": "Italy",
                            "name_ru": None
                        }
                    }
                },
                "subcategory": {
                    "name": "Red",
                    "name_ru": None,
                    "category": {
                        "name": "Wine",
                        "name_ru": None
                    }
                },
                "foods": [
                    {
                        "name": "Game (venison, birds)",
                        "name_ru": "С дичью"
                    },
                    {
                        "name": "Lamb",
                        "name_ru": "Бараниной"
                    }
                ],
                "varietals": [
                    {
                        "varietal": {
                            "name": "Cabernet Sauvignon",
                            "name_ru": "Каберне Совиньон"
                        },
                        "percentage": 85.0
                    },
                    {
                        "varietal": {
                            "name": "Cabernet Franc",
                            "name_ru": "Каберне Фран"
                        },
                        "percentage": 15.0
                    }
                ]
            },
            "count": 0,
            "image_path": "-Lymluc5yKRoLQyYLbJG.png"
        }}
    assert dict1 == dict2
