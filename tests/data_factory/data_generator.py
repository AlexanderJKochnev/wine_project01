# flake8: noqa: E121
# tests/data_factory/data_generator.py
from typing import Type, Dict, Any, Union, List
from app.support.drink.schemas import DrinkRead, DrinkCreate, DrinkUpdate, BaseModel
from pathlib import Path
import json
from tests.data_factory.fake_generator import TestDataGenerator

""" открыть swagger и скопировать json response 200 get_by_id """


def json_reader(schema: str = 'drink',
                filename: str = 'data.json',
                input_dir: str = '') -> dict:
    """ читает json file """
    try:
        source = Path(__file__).resolve().parent.joinpath(
            input_dir, filename
            )
        if source.exists():
            with open(source) as f:
                data = json.load(f)
            if isinstance(data, dict):
                return data.get(schema)
    except Exception as e:
        print(f'Json_reader error: {e}')
        return None


def remove_id(data: Any) -> dict:
    if not isinstance(data, dict):
        return data
    data.pop('id', None)
    data.pop('additionalProp1', None)
    for key, val in data.items():
        if isinstance(val, dict):
            data[key] = remove_id(val)
        if isinstance(val, list):
            data[key] = [remove_id(x) for x in val]
    return data

# ---------------------


def get_relations(data: dict) -> list:
    """ сортировка ключей по вложенности"""
    tmp: dict = {key: val for key, val in data.items() if isinstance(val, Union[Dict, List])}
    return tmp

generator = TestDataGenerator()
template = remove_id(json_reader())
data = generator.generate(template, count=5)
# 1. отфильторовать все вложенные словари

def get_nested(d: dict, path: str) -> Any:
    """
    Получить значение из вложенного словаря по пути с точками.

    Пример:
        get_nested(data, 'subregion_id.region.country.name') -> 'Spain'
        get_nested(data, 'subregion_id.region.country') -> {'name': 'Spain', ...}

    Если ключ не найден — возвращает None.
    """
    keys = path.split('.')
    current: Any = d
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None  # Ключ не найден
    return current


def set_nested(
    d: dict,
    path: str,
    value: Any,
    create_missing: bool = True,
    replace_primitive: bool = True
) -> None:
    """
    Установить значение по вложенному пути с точками.

    Поддерживает:
      - создание промежуточных словарей (create_missing)
      - замену примитивов на словари (replace_primitive)

    Пример:
        d = {'a': 'string'}
        set_nested(d, 'a.b.c', 42, create_missing=True, replace_primitive=True)
        → d == {'a': {'b': {'c': 42}}}
    """
    keys = path.split('.')
    current = d
    parent = None
    parent_key = None

    for key in keys[:-1]:
        parent = current
        parent_key = key

        # Проверяем, что parent — словарь
        if not isinstance(parent, dict):
            if replace_primitive:
                # Заменяем примитив на словарь
                if isinstance(parent, dict) or parent is d:
                    # Это невозможно, логическая ошибка
                    pass
                raise TypeError(f"Parent is not a dict: {repr(parent)}")
            else:
                raise TypeError(f"Cannot access '{key}' — parent is not a dict: {repr(parent)}")

        if key in parent:
            current = parent[key]
            # Проверим, что current — словарь или можно создать
            if isinstance(current, dict):
                continue
            elif create_missing and replace_primitive:
                # Заменяем примитив на словарь
                parent[key] = {}
                current = parent[key]
            elif create_missing:
                raise TypeError(f"Cannot descend into '{key}' — value is {type(current).__name__}, not dict")
            else:
                raise KeyError(f"Key '{key}' exists but is not dict and create_missing=False")
        else:
            if create_missing:
                parent[key] = {}
                current = parent[key]
            else:
                raise KeyError(f"Key '{key}' not found and create_missing=False")

    # Теперь устанавливаем финальное значение
    final_key = keys[-1]

    if not isinstance(current, dict):
        if replace_primitive:
            # Заменяем текущий уровень (если он в словаре-родителе) на {}
            if isinstance(parent, dict) and parent_key is not None:
                parent[parent_key] = {}
                current = parent[parent_key]
            else:
                # current — это сам корень d, и он не dict
                if d is current and replace_primitive:
                    # Но d — аргумент функции, и мы не можем его переназначить
                    raise TypeError(
                        "Cannot replace root object if it's not a dict. Pass a dict as root."
                    )
                else:
                    raise TypeError(f"Cannot assign to '{final_key}' — parent is not a dict: {repr(current)}")
        else:
            raise TypeError(f"Cannot assign to '{final_key}' — parent is not a dict: {repr(current)}")

    current[final_key] = value


def get_all_dict_paths(data: Any, parent_path: str = "") -> list[str]:
    paths: list[str] = []

    if isinstance(data, dict):
        # Только если это НЕ корень, добавляем текущий путь
        # (корень — это сам data, и мы его не считаем "вложенным")
        if parent_path:
            paths.append(parent_path)

        for key, value in data.items():
            child_path = f"{parent_path}.{key}" if parent_path else key
            if isinstance(value, (dict, list)):
                paths.extend(get_all_dict_paths(value, child_path))

    elif isinstance(data, list):
        for idx, item in enumerate(data):
            list_path = f"{parent_path}[{idx}]"
            if isinstance(item, (dict, list)):
                paths.append(list_path)
                # Рекурсивно ищем внутри, но НЕ добавляем list_path повторно
                sub_paths = get_all_dict_paths(item, list_path)
                # Исключаем сам list_path из подпутей
                paths.extend(p for p in sub_paths if p != list_path)

    result =  sorted(paths, key=lambda p: p.count('.') + p.count('['), reverse=True)
    return {x: x.split('.')[-1].replace('_id','').split('[', 1)[0]  for x in result}
    
# single = get_relations(data[0])
# print(json.dumps(single, indent=2, ensure_ascii=False))
# result = get_all_dict_paths(single)
# print(json.dumps(result, indent=2, ensure_ascii=False))
print('==============================')
single = data[0]
result = get_all_dict_paths(single)
print(json.dumps(result, indent=2, ensure_ascii=False))
print('==============================')
# result = [(x, x.split('.')[-1].replace('_id', '').split('[', 1)[0]) for x in result]
print(json.dumps(single, indent=2, ensure_ascii=False))
print('===============================')
from app.core.utils.common_utils import get_nested as gett
nested = gett(single, 'subregion_id.region.country')
print(json.dumps(nested, indent=2, ensure_ascii=False))