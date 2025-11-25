from copy import deepcopy
from typing import Optional

from pydantic import BaseModel, ValidationError
from app.core.config.project_config import settings
from app.core.utils.common_utils import jprint
from app.core.utils.converters import (drink_level, field_cast, get_subcategory, get_subregion,
                                       read_json_by_keys, get_pairing, parse_grapes, convert_varietals,
                                       root_level, split_outside_parentheses, string_to_float,
                                       remove_redundant, convert_custom, read_convert_json,
                                       get_varietal, string_to_int, split_outside_parentheses_multi)
from app.core.utils.io_utils import get_filepath_from_dir_by_name
from app.support.item.schemas import DrinkCreateRelation, ItemCreateRelation

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


class Name(BaseModel):
    name: str
    name_ru: Optional[str] = None


class Varietal(BaseModel):
    percentage: int
    varietal: Name


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


def test_parse_grapes():
    datas = {"Pinot Noir 40-45%, Meunier 10-15%, Chardonnay 40%.":
                 {"Pinot Noir": 42, "Meunier": 12, "Chardonnay": 40},
             "Сabernet Sauvignon 91%, Merlot 6%, Petit Verdot 2%, Malbec 1%.":
                 {"Сabernet Sauvignon": 91, "Merlot": 6, "Petit Verdot": 2, "Malbec": 1},
             "\"каберне совиньон\" 91%, \"мерло\" 6%, \"пти вердо\" 2%, \"мальбек\" 1%.":
                 {"Каберне Совиньон": 91, "Мерло": 6, "Пти Вердо": 2, "Мальбек": 1},
             "Sauvignon Blanc 100%.": {"Sauvignon Blanc": 100},
             "совиньон блан 100%.": {"Совиньон Блан": 100},
             "Sangiovese Capannelle 50%, Merlot Avignonesi 50%.":
                 {"Sangiovese Capannelle": 50, "Merlot Avignonesi": 50},
             "\"санджовезе капаннелле\" 50%, \"мерло авигнонеси» 50%.":
                 {"Санджовезе Капаннелле": 50, "Мерло Авигнонеси": 50},
             "\"каберне совиньон\" 79%, \"мерло\" 10%, \"каберне фран\" 10%, \"пти вердо\" 1%.":
                 {"Каберне Совиньон": 79, "Мерло": 10, "Каберне Фран": 10, "Пти Вердо": 1},
             "\"мерло\" 70%, \"каберне совиньон\" 15%, \"каберне фран\" 15%.":
                 {"Мерло": 70, "Каберне Совиньон": 15, "Каберне Фран": 15},
             "Grenache, Senso, Shiraz (Syrah).":
                 {"Grenache": 34, "Senso": 33, "Shiraz (Syrah)": 33},
             "\"гренаш\", \"сенсо\", \"шираз\" (\"сира\").":
                 {"Гренаш": 34, "Сенсо": 33, "Шираз (Сира)": 33}
             }
    for key, val in datas.items():
        result = parse_grapes(key)
        assert result == val, key


def test_convert_varietals():
    data = {"name": {"Сabernet Sauvignon": 91,
                     "Merlot": 6,
                     "Petit Verdot": 2,
                     "Malbec": 1},
            "name_ru": {"Каберне Совиньон": 91,
                        "Мерло": 6,
                        "Пти Вердо": 2,
                        "Мальбек": 1}
            }
    expected = [{"varietal": {"name": "Сabernet Sauvignon",
                              "name_ru": "Каберне Совиньон"},
                 "percentage": 91},
                {"varietal": {"name": "Merlot",
                              "name_ru": "Мерло"},
                 "percentage": 6},
                {"varietal": {"name": "Petit Verdot",
                              "name_ru": "Пти Вердо"},
                 "percentage": 2},
                {"varietal": {"name": "Malbec",
                              "name_ru": "Мальбек"},
                 "percentage": 1}
                ]
    result = convert_varietals(data)
    assert result == expected


def test_read_json_file():
    """ чтение файла с данными """
    filepath = get_filepath_from_dir_by_name(filename)
    #   НАСТРОЙКИ
    # Конвертируемые поля (остальные поля имеют исходный формат){'vol': 'float', 'count': 'int', 'alc': 'float'}
    casted_fields: dict = settings.casted_fields
    # Поля верхнего уровня ('vol', 'count', 'image_path', 'image_id' остальные поля в drink
    first_level_fields: list = settings.first_level_fields
    language_key = settings.language_key
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
        # 0. проверка корневого уровня root_level
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
        # 1. проверка уровня drink
        result: dict = drink_level(source, casted_fields, language_key)
        drink_dict: dict = result
        # 2. проверка get_subregion
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

        # 3. проверка get_subcategory
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

        # 4. проверка get_pairing
        try:
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
            jprint(root_dict)
            print('========')
            for key, val in drink_dict.items():
                print(f'{key}:  {val}')
            # ===================
            assert False, f'ошибка в методе: get_pairing: {e}'
        # 5. проверка get_varietals
        try:
            x = get_varietal(drink_dict, language_key)
            if not x:
                raise Exception('функция get_varietal провалилась')
            result: list = drink_dict.get('varietals')
            if result:
                for item in result:
                    _ = Varietal(**item)
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
            assert False, 'ошибка валидации в методе: get_varietal'
        except Exception as e:
            jprint(root_dict)
            print('========')
            for key, val in drink_dict.items():
                print(f'{key}:  {val}')
            assert False, f'ошибка в методе: get_pairing: {e}'
        """
        if '-LymvdWInXSaNmZ1Jx04' in root_dict.get('image_path'):
            jprint(root_dict)
            for key, val in drink_dict.items():
                print(key, val)
            assert False
        """
        # 6. remove redundant
        redundant_fields = settings.redundant
        result = remove_redundant(root_dict, redundant_fields)
        assert result, 'ошибка метода remove_redundant'
        # 7. DrinkCreateRelation Validation
        try:
            # 7. DrinkCreateRelation Validation
            drink_dict = {key.lower(): val for key, val in drink_dict.items()}
            drink = DrinkCreateRelation.model_validate(drink_dict)
            drink_back = drink.model_dump(exclude_unset=True)
            root_dict['drink'] = drink_back
            root = ItemCreateRelation.model_validate(root_dict)
            final_result = root.model_dump(exclude_unset=True)
            assert final_result == root_dict
            # raise Exception('just for look at datas')
        except ValidationError as exc:
            for error in exc.errors():
                print(f"  Место ошибки (loc): {error['loc']}")
                print(f"  Сообщение (msg): {error['msg']}")
                print(f"  Тип ошибки (type): {error['type']}")
                # input_value обычно присутствует в словаре ошибки
                if 'input_value' in error:
                    print(f"  Некорректное значение (input_value): {error['input_value']}")
                print("-" * 20)
            assert False, 'ошибка валидации в методе: get_varietal'
        except Exception as e:
            jprint(root_dict)
            print('========')
            for key, val in drink_dict.items():
                print(f'{key}:  {val}')
            assert False, f'ошибка в DrinkCreateRelation Validation: {e}'
        result = convert_custom(value)
        if result != final_result:
            jprint(result)
        assert result == final_result

    # print(f'количество обработанных записей {n}')
    # jprint(root_dict)
    # for key, val in drink_dict.items():
    #     print(key, val)
    # assert False


def test_read_convert_json():
    """
        тестирование функции read_convert_json
        считывание по элементно и декодирование файла json
    """
    # filename: str = 'data.json'
    for n, result in read_convert_json(filename):
        result_validated = ItemCreateRelation.validate(result)
        back_dict = result_validated.model_dump(exclude_unset=True)
        assert result == back_dict, f"вол-во записей {n}"