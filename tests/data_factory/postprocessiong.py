# tests/data_factory/postprocessing.py
import random

def validate_and_fix_numeric_ranges(data, int_range=None, float_range=None):
    """
    Рекурсивно валидирует и исправляет значения int и float в словаре/списке,
    заменяя несоответствующие значения на случайные в заданных диапазонах.

    :param data: Словарь, список или вложенные структуры
    :param int_range: tuple (min, max) для значений типа int
    :param float_range: tuple (min, max) для значений типа float
    :return: Изменённая структура данных
    """
    if int_range is None:
        int_range = (0, 100)
    if float_range is None:
        float_range = (0.0, 1.0)

    int_min, int_max = int_range
    float_min, float_max = float_range

    def fix_value(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if not (int_min <= value <= int_max):
                return random.randint(int_min, int_max)
        elif isinstance(value, float):
            if not (float_min <= value <= float_max):
                return random.uniform(float_min, float_max)
        return value

    def traverse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    traverse(value)
                else:
                    fixed_value = fix_value(value)
                    if fixed_value != value:
                        obj[key] = fixed_value
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                if isinstance(item, (dict, list)):
                    traverse(item)
                else:
                    fixed_value = fix_value(item)
                    if fixed_value != item:
                        obj[i] = fixed_value

    traverse(data)
    return data
