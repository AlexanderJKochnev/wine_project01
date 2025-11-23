# app/core/utils/converters.py
import re
from typing import Dict, Any, List, Optional, Union
from app.core.utils.io_utils import get_filepath_from_dir_by_name
import ijson
from copy import deepcopy
from app.core.config.project_config import settings


def detect_json_structure(filename):
    """
    определяет где находятся нужные записи
    в корне или на 2 уровне
    """
    with open(filename, 'rb') as file:
        parser = ijson.parse(file)
        try:
            # Первое событие — обычно 'start_map' для корня
            prefix, event, value = next(parser)
            if event == 'start_map':
                # Следующее событие — либо ключ корня, либо конец
                prefix, event, value = next(parser)
                if event == 'map_key':
                    if value in ['items', 'item']:
                        return value
                    else:
                        # Это ключ корневого уровня, значит, словари на первом уровне
                        return ''
        except StopIteration:
            pass
    return None


def read_json_by_keys(filename: str):
    """
        парсит json файл по одному значению (экономия памяти)
    """
    path = detect_json_structure(filename)
    if path is None:
        raise ValueError("Не удалось определить структуру JSON-файла")

    with open(filename, 'rb') as file:
        # Итерируемся по парам (ключ, значение) на корневом уровне
        for key, value in ijson.kvitems(file, path):
            yield key, value


def batch_convert_data(filename: str = 'data.json') -> Dict[str, Any]:
    try:
        # 1. получение пути к файлу с данными
        filepath = get_filepath_from_dir_by_name(filename)
        # 2. чтение json файла и преобразование его в dict
        # dict1 = readJson(filepath)
        # 3. основной цикл
        # 3.1. проверяем где находятся записи
        m = 0
        for n, (key, value) in enumerate(read_json_by_keys(filepath)):
            if isinstance(value, dict):
                convert_custom(value)
                m += 1
        print(f'обработано {m} записей')
    except Exception as e:
        # перехватит в fastapi
        raise Exception(e)


def convert_custom(dict1: Dict[str, Any]) -> Dict[str, Any]:
    """
        Конвертирует словарь 1 в словарь 2 согласно заданным правилам.
        Валидирует pymodel = ItemCreateRelation(**item)
            back_item = pymodel.model_dump(exclude_unset=True)
            assert item == back_item
    """
    source = deepcopy(dict1)
    # Определяем поля, которые нужно игнорировать ('index', 'isHidden', 'imageTimestamp')
    ignored_fields: list = settings.ignored_fields
    # Интернацинальные поля ('vol', 'alc', 'count')
    international_fields = settings.international_fields
    # Конвертируемые поля (остальные поля имеют исходный формат){'vol': 'float', 'count': 'int', 'alc': 'float'}
    casted_fields: dict = settings.casted_fields
    # Поля верхнего уровня (остальные поля в drink ('vol', 'count', 'image_path', 'image_id', 'uid')
    first_level_fields: list = settings.first_level_fields
    # сложные поля ('country', 'category', 'region', 'pairing', 'varietal')
    complex_fields = settings.complex_fields
    language_key: dict = settings.language_key  # {english: en, ...}
    intl_fields = [val for val in international_fields if val not in first_level_fields]
    # delimiter1
    delim = settings.RE_DELIMITER
    # result dict root level
    item_dict: dict = {}
    # second level dict
    drink_dict: dict = {}
    # 0. make root level dict
    item_dict.update(root_level(source, first_level_fields, casted_fields))
    # 1. make drink level with simple fields
    drink_dict.update(drink_level(source, casted_fields, language_key))
    # 2. country->region->subregion
    get_subregion(drink_dict, language_key, delim)
    # 3. subcategory->category
    get_subcategory(drink_dict, language_key, delim)
    return item_dict


def get_pairing(drink_dict: dict, language_key: str,
                delim: str) -> bool:
    try:
        foods = dict_pop(drink_dict, 'pairing')
        if foods:
        
    except Exception as e:
        print(f'get_pairing.error: {e}')


def get_subregion(drink_dict: dict, language_key: str,
                  delim: str) -> bool:
    """
        формируем subregion->region->country
    """
    try:
        country = dict_pop(drink_dict, 'country')
        subregion = {"region": {"country": {"name": country.capitalize() if country else country}}}
        for lang in language_key.values():
            tmp = dict_pop(drink_dict, f'region{lang}')
            region, sub = split_outside_parentheses(tmp, delim)
            subregion[f'name{lang}'] = sub.capitalize() if sub else None
            subregion['region'][f'name{lang}'] = region.capitalize() if region else None
        drink_dict['subregion'] = subregion
        return True
    except Exception as e:
        print(f'get_subregion.error: {e}')


def get_subcategory(drink_dict: dict, language_key: str,
                    delim: str) -> bool:
    """
    формируем subcategory->category
    """
    try:
        wine_category = settings.wine_category
        print(f'{wine_category=}')
        category = dict_pop(drink_dict, 'category')
        if category in wine_category:
            subcat, category = category.capitalize(), 'Wine'
            subcategory = {"name": subcat, "category": {"name": category}}
        else:
            subcategory = {"category": {"name": category}}
            for lang in language_key.values():
                tmp = dict_pop(drink_dict, f'type{lang}')
                subcat = tmp.capitalize() if tmp else None
                subcategory[f'name{lang}'] = subcat
        drink_dict['subcategory'] = subcategory
        return True

    except Exception as e:
        print(f'get_category.error: {e}')
        return False


def split_outside_parentheses(text: str, separators=',.:;') -> List:
    """
    Разделяет строку по первому найденному разделителю (из списка ',.:;'),
    который находится **вне скобок** `()`.
    Возвращает список из двух частей (до и после разделителя).
    Если разделителей вне скобок нет — возвращает список с одной строкой
    (без изменений, но с удалёнными пробелами по краям) + None.
    """
    if not text:
        return [None, None]

    depth = 0  # уровень вложенности скобок
    for i, char in enumerate(text):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
            # Защита от отрицательной глубины (например, ")abc")
            if depth < 0:
                depth = 0
        elif depth == 0 and char in separators:
            # Найден разделитель вне скобок
            left = text[:i].strip(f' {separators}:')
            right = text[i + 1:].strip(f' {separators}:')
            return [left, right]

    # Разделителей вне скобок не найдено
    return [text.strip(), None]


def drink_level(source: dict, casted_fields: dict, language_key: dict) -> dict:
    result: dict = {}
    for key, val in source.items():
        if isinstance(val, dict):
            suffix = language_key[key]
            for k2, v2 in val.items():
                result[f'{k2}{suffix}'] = field_cast(k2, v2, casted_fields)
        else:
            result[key] = field_cast(key, val, casted_fields)
    return result


def root_level(source: dict, first_level_fields: tuple, casted_fields: dict) -> dict:
    """
        собирает словарь корневого уровня
    """
    newdict: dict = {}
    for val in first_level_fields:
        value = dict_find(source, val)
        if val in casted_fields.keys():
            value = field_cast(val, value, casted_fields)
            newdict[val] = value
        if val == 'uid':
            newdict['image_path'] = f'{dict_find(source, 'uid')}.png'
    return newdict


def field_cast(field_name: str, val: Any, casted_fields: dict) -> Union[float, int, str]:
    """
    преобразует значение в требуемый тип
    """
    try:
        casting = casted_fields.get(field_name)
        match casting:
            case 'float':
                result = string_to_float(val)
            case 'int':
                result = string_to_int(val)
            case _:
                result = val
        return result
    except Exception as e:
        print(f'field_cast.error: {e}')


def string_to_float(s: str) -> float:
    """
    Преобразует строку в float, удаляя все символы кроме цифр и точки,
    заменяя запятую на точку.
    """
    if not s:
        return 0.0
    if isinstance(s, float):
        return s
    # Заменяем запятую на точку
    s = s.replace(',', '.')

    # Оставляем только цифры и точки
    cleaned = ''.join(c for c in s if c.isdigit() or c == '.')

    # Удаляем лишние точки (оставляем только первую)
    parts = cleaned.split('.')
    if len(parts) > 1:
        cleaned = parts[0] + '.' + ''.join(parts[1:])

    try:
        return float(cleaned) if cleaned else 0.0
    except ValueError:
        return 0.0


def float_to_int(f: float) -> int:
    try:
        # float, округляем по математическим правилам, затем в int
        return int(round(f)) if f else 0
    except ValueError:
        return 0


def string_to_int(s: Any) -> int:
    if isinstance(s, int):
        return s
    return float_to_int(string_to_float(s))


def dict_find(d, key):
    """
    Ищет ключ в многоуровневом словаре и возвращает значение, если найден.
    Возвращает None, если ключ не найден.
    """
    if not isinstance(d, dict):
        return None

    if key in d:
        return d[key]

    for k, v in d.items():
        if isinstance(v, dict):
            result = dict_find(v, key)
            if result is not None:
                return result
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    result = dict_find(item, key)
                    if result is not None:
                        return result
    return None


def dict_pop(d, key):
    """
    Ищет и удаляет ключ в многоуровневом словаре, возвращает значение, если найден.
    Возвращает None, если ключ не найден.
    """
    if not isinstance(d, dict):
        return None

    if key in d:
        return d.pop(key)

    for k, v in d.items():
        if isinstance(v, dict):
            result = dict_pop(v, key)
            if result is not None:
                return result
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    result = dict_pop(item, key)
                    if result is not None:
                        return result
    return None


# ==========================
def convert_dict1_to_dict2(dict1: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертирует словарь 1 в словарь 2 согласно заданным правилам.
    """
    dict2 = {}

    # Определяем поля, которые нужно игнорировать
    ignored_fields = {'index', 'isHidden', 'uid', 'imageTimestamp'}

    for key, value in dict1.items():
        new_entry = {}

        # Сохраняем category и country для дальнейшего использования
        category = value.get('category', '')
        country = value.get('country', '')

        # Копируем все неигнорируемые поля
        for field, field_value in value.items():
            if field not in ignored_fields:
                if field == 'english':
                    # Обрабатываем английские данные
                    english_data = value.get('english', {})
                    russian_data = value.get('russian', {})

                    drink = {}

                    # Копируем основные поля
                    for eng_key, eng_val in english_data.items():
                        if eng_key == 'vol':
                            # Конвертируем объем
                            vol_str = str(eng_val).lower()
                            vol_match = re.search(r'(\d+\.?\d*)\s*(l|ml)', vol_str)
                            if vol_match:
                                vol_num = float(vol_match.group(1))
                                unit = vol_match.group(2)
                                if unit == 'ml':
                                    vol_num = vol_num / 1000.0
                            else:
                                vol_num = 0.0
                            if key not in dict2:
                                dict2[key] = {}
                            dict2[key]['vol'] = vol_num
                        elif eng_key == 'region':
                            # Обработка региона
                            drink['subregion'] = parse_region(eng_val, russian_data.get('region', ''))
                        elif eng_key == 'category':
                            # Обработка категории
                            drink['subcategory'] = parse_category(eng_val, english_data.get('type', ''))
                        elif eng_key == 'pairing':
                            # Обработка pairing
                            drink['foods'] = parse_pairing(eng_val, russian_data.get('pairing', ''))
                        elif eng_key == 'varietal':
                            # Обработка varietal
                            drink['varietals'] = parse_varietal(eng_val, russian_data.get('varietal', ''))
                        elif eng_key == 'madeOf':
                            drink['madeof'] = eng_val
                        elif eng_key == 'type':
                            # Не добавляем type отдельно, он уже обработан в категории
                            pass
                        else:
                            drink[eng_key] = eng_val

                    # Добавляем русские данные
                    for rus_key, rus_val in russian_data.items():
                        if rus_key == 'region':
                            # Обработка региона для русского языка уже сделана
                            continue
                        elif rus_key == 'category':
                            # Категория не нужна отдельно
                            continue
                        elif rus_key == 'pairing':
                            # pairing уже обработан
                            continue
                        elif rus_key == 'varietal':
                            # varietal уже обработан
                            continue
                        elif rus_key == 'madeOf':
                            drink['madeof_ru'] = rus_val
                        elif rus_key == 'type':
                            # type уже обработан
                            continue
                        else:
                            drink[f"{rus_key}_ru"] = rus_val

                    new_entry['drink'] = drink
                elif field == 'count':
                    new_entry[field] = field_value
                elif field == 'country':
                    # Обрабатываем страну в регионе
                    english_data = value.get('english', {})
                    russian_data = value.get('russian', {})
                    if 'drink' in new_entry:
                        if 'subregion' not in new_entry['drink']:
                            new_entry['drink']['subregion'] = {'name': None, 'name_ru': None,
                                                               'region': {'name': None, 'name_ru': None,
                                                                          'country': {'name': capitalize_country_name(field_value), 'name_ru': None}}}
                        else:
                            # Устанавливаем страну в регион
                            new_entry['drink']['subregion']['region']['country']['name'] = capitalize_country_name(
                                field_value
                            )
                elif field == 'uid':
                    # Используем UID для image_path
                    new_entry['image_path'] = f"{field_value}.png"

        # Устанавливаем count в None, если его нет и не было в исходном
        if 'count' not in new_entry:
            new_entry['count'] = None

        # Устанавливаем vol в None, если его нет
        if 'vol' not in new_entry:
            new_entry['vol'] = None

        dict2[key] = new_entry

    return dict2


def convert_dict2_to_dict1(dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Конвертирует словарь 2 в словарь 1 (обратная конвертация).
    """
    dict1 = {}

    for key, value in dict2.items():
        new_entry = {}

        # Восстанавливаем UID из image_path
        if 'image_path' in value:
            image_path = value['image_path']
            uid = image_path.replace('.png', '') if image_path.endswith('.png') else image_path
            new_entry['uid'] = uid

        # Восстанавливаем count
        if 'count' in value and value['count'] is not None:
            new_entry['count'] = value['count']

        # Восстанавливаем vol
        if 'vol' in value and value['vol'] is not None:
            vol = value['vol']
            # Преобразуем обратно в строку в формате "X.XX l"
            vol_str = f"{vol} l"
            if 'english' not in new_entry:
                new_entry['english'] = {}
                new_entry['russian'] = {}
            new_entry['english']['vol'] = vol_str
            new_entry['russian']['vol'] = vol_str

        # Обрабатываем drink
        if 'drink' in value:
            drink = value['drink']
            english_data = {}
            russian_data = {}

            for field, field_value in drink.items():
                if field == 'subregion':
                    # Восстанавливаем region
                    region_en = reconstruct_region_en(drink['subregion'])
                    region_ru = reconstruct_region_ru(drink['subregion'])
                    english_data['region'] = region_en
                    russian_data['region'] = region_ru

                    # Восстанавливаем страну из country в регионе
                    country_name = drink['subregion']['region']['country']['name']
                    if country_name:
                        new_entry['country'] = country_name.lower()
                elif field == 'subcategory':
                    # Восстанавливаем category
                    category_info = reconstruct_category(drink['subcategory'])
                    new_entry['category'] = category_info['category']  # Добавляем в основной словарь
                    english_data['category'] = category_info['category']  # Также добавляем в english
                    if category_info['type']:
                        english_data['type'] = category_info['type']
                elif field == 'foods':
                    # Восстанавливаем pairing
                    pairing_en, pairing_ru = reconstruct_pairing(drink['foods'])
                    english_data['pairing'] = pairing_en
                    russian_data['pairing'] = pairing_ru
                elif field == 'varietals':
                    # Восстанавливаем varietal
                    varietal_en, varietal_ru = reconstruct_varietal(drink['varietals'])
                    english_data['varietal'] = varietal_en
                    russian_data['varietal'] = varietal_ru
                elif field == 'madeof':
                    english_data['madeOf'] = field_value
                elif field == 'madeof_ru':
                    russian_data['madeOf'] = field_value
                else:
                    # Обрабатываем обычные поля
                    if field.endswith('_ru'):
                        # Русская версия
                        base_field = field[:-3]
                        russian_data[base_field] = field_value
                    else:
                        # Английская версия
                        english_data[field] = field_value

            new_entry['english'] = english_data
            new_entry['russian'] = russian_data

            # Если страна не была установлена из региона, устанавливаем из country
            if 'country' not in new_entry and 'subregion' in drink and 'region' in drink['subregion'] and 'country' in \
                    drink['subregion']['region']:
                country_name = drink['subregion']['region']['country']['name']
                if country_name:
                    new_entry['country'] = country_name.lower()

        # Если country не установлен, используем значение по умолчанию
        if 'country' not in new_entry:
            new_entry['country'] = 'unknown'

        dict1[key] = new_entry

    return dict1


def parse_region(region_en: str, region_ru: str) -> Dict[str, Any]:
    """Парсит регион и субрегион из строки."""
    # Разделители: запятая или точка
    parts_en = re.split(r'[,.]', region_en)
    parts_ru = re.split(r'[,.]', region_ru)

    # Удаляем лишние пробелы
    parts_en = [part.strip() for part in parts_en if part.strip()]
    parts_ru = [part.strip() for part in parts_ru if part.strip()]

    if len(parts_en) >= 2:
        subregion_en = parts_en[-1]
        region_en_clean = parts_en[-2]
    else:
        subregion_en = None
        region_en_clean = parts_en[0] if parts_en else None

    if len(parts_ru) >= 2:
        subregion_ru = parts_ru[-1]
        region_ru_clean = parts_ru[-2]
    else:
        subregion_ru = None
        region_ru_clean = parts_ru[0] if parts_ru else None

    return {'name': subregion_en, 'name_ru': subregion_ru,
            'region': {'name': region_en_clean, 'name_ru': region_ru_clean,
                       'country': {'name': None,  # Будет установлено позже
                                   'name_ru': None}}}


def parse_category(category: str, type_val: str = None) -> Dict[str, Any]:
    """Парсит категорию и подкатегорию."""
    category_lower = category.lower()

    if category_lower in ['red', 'white', 'rose', 'sparkling', 'port']:
        subcategory_name = capitalize_first_letter(category_lower)
        return {'name': subcategory_name, 'name_ru': None, 'category': {'name': 'Wine', 'name_ru': None}}
    elif category_lower in ['vodka', 'cognac', 'whiskey', 'tequila', 'rum', 'beer']:
        subcategory_name = capitalize_first_letter(category_lower)
        return {'name': None, 'name_ru': None, 'category': {'name': subcategory_name, 'name_ru': None}}
    elif category_lower == 'other':
        # Используем type для подкатегории
        if type_val:
            # Убираем точки и другие символы из type
            clean_type = type_val.replace('.', '').strip()
            # Определяем русское имя (простое преобразование)
            type_ru = get_russian_name(clean_type)
            return {'name': clean_type, 'name_ru': type_ru, 'category': {'name': 'Other', 'name_ru': None}}
        else:
            return {'name': None, 'name_ru': None, 'category': {'name': 'Other', 'name_ru': None}}
    else:
        # Неизвестная категория - по умолчанию Wine
        return {'name': None, 'name_ru': None, 'category': {'name': 'Wine', 'name_ru': None}}


def parse_pairing(pairing_en: str, pairing_ru: str) -> List[Dict[str, str]]:
    """Парсит pairing в список еды."""
    # Разделяем по запятой, но не внутри скобок
    foods_en = split_preserving_brackets(pairing_en)
    foods_ru = split_preserving_brackets(pairing_ru)

    result = []
    for i, food_en in enumerate(foods_en):
        food_en = food_en.strip()
        if food_en:
            food_ru = foods_ru[i].strip() if i < len(foods_ru) else None
            result.append(
                {'name': food_en, 'name_ru': food_ru}
            )

    return result


def parse_varietal(varietal_en: str, varietal_ru: str) -> List[Dict[str, Any]]:
    """Парсит varietal в список сортов."""
    varietals_en = parse_varietal_string(varietal_en)
    varietals_ru = parse_varietal_string(varietal_ru)

    result = []
    for i, (var_en, perc_en) in enumerate(varietals_en):
        var_ru, perc_ru = varietals_ru[i] if i < len(varietals_ru) else (None, None)

        # Если процент не указан, распределяем равномерно
        if perc_en is None:
            if len(varietals_en) == 1:
                perc_en = 100.0
            else:
                perc_en = round(100.0 / len(varietals_en), 1)

        result.append(
            {'varietal': {'name': var_en, 'name_ru': var_ru}, 'percentage': perc_en}
        )

    return result


def split_preserving_brackets(text: str) -> List[str]:
    """Разделяет строку по запятым, но не внутри скобок."""
    if not text:
        return []

    result = []
    bracket_level = 0
    current = ''

    for char in text:
        if char == '(':
            bracket_level += 1
            current += char
        elif char == ')':
            bracket_level -= 1
            current += char
        elif char == ',' and bracket_level == 0:
            result.append(current.strip())
            current = ''
        else:
            current += char

    if current:
        result.append(current.strip())

    return result


def parse_varietal_string(varietal_str: str) -> List[tuple]:
    """Парсит строку varietal, извлекая названия сортов и проценты."""
    if not varietal_str:
        return []

    # Паттерн для поиска "название X%" или "название X.X%"
    pattern = r'(["\']?)([^"\',%]+(?:\([^)]*\))?[^"\',%]*)\1\s*(\d+\.?\d*)%?'
    matches = re.findall(pattern, varietal_str)

    result = []
    for _, name_part, percentage_str in matches:
        # Убираем лишние пробелы и кавычки
        name = name_part.strip()
        percentage = float(percentage_str) if percentage_str else None
        result.append((name, percentage))

    # Если не найдены подходящие паттерны, разделяем по запятым
    if not result:
        parts = re.split(r',', varietal_str)
        for part in parts:
            part = part.strip()
            if part:
                # Проверяем, есть ли процент в этой части
                perc_match = re.search(r'(\d+\.?\d*)%$', part)
                if perc_match:
                    name_part = part[:perc_match.start()].strip()
                    name = name_part.strip()
                    percentage = float(perc_match.group(1))
                else:
                    name = part.strip()
                    percentage = None
                result.append((name, percentage))

    return result


def capitalize_first_letter(s: str) -> str:
    """Делает первую букву заглавной."""
    if not s:
        return s
    return s[0].upper() + s[1:]


def capitalize_country_name(country: str) -> str:
    """Приводит название страны к нормальному виду."""
    if not country:
        return country
    # Заменяем подчеркивания на пробелы и делаем заглавные буквы
    parts = country.split('_')
    return ' '.join([part.capitalize() for part in parts])


def get_russian_name(english_name: str) -> str:
    """Простое преобразование английского названия в русское."""
    translations = {'calvados': 'Кальвадос', 'sake': 'Cакэ', 'vodka': 'Водка', 'cognac': 'Коньяк', 'whiskey': 'Виски',
                    'tequila': 'Текила', 'rum': 'Ром', 'beer': 'Пиво', 'red': 'Красное', 'white': 'Белое', 'rose': 'Розовое',
                    'sparkling': 'Игристое', 'port': 'Портвейн'}
    return translations.get(english_name.lower(), None)


def reconstruct_region_en(subregion_data: Dict[str, Any]) -> str:
    """Восстанавливает строку региона из структуры."""
    subregion = subregion_data.get('name')
    region = subregion_data.get('region', {}).get('name')

    if subregion and region:
        return f"{region}, {subregion}"
    elif region:
        return region
    else:
        return ""


def reconstruct_region_ru(subregion_data: Dict[str, Any]) -> str:
    """Восстанавливает строку региона на русском из структуры."""
    subregion = subregion_data.get('name_ru')
    region = subregion_data.get('region', {}).get('name_ru')

    if subregion and region:
        return f"{region}, {subregion}"
    elif region:
        return region
    else:
        return ""


def reconstruct_category(subcategory_data: Dict[str, Any]) -> Dict[str, str]:
    """Восстанавливает категорию и тип из структуры."""
    category_name = subcategory_data.get('category', {}).get('name', '').lower()

    # Определяем основную категорию
    if category_name == 'wine':
        sub_name = subcategory_data.get('name', '').lower()
        if sub_name in ['red', 'white', 'rose', 'sparkling', 'port']:
            return {'category': sub_name, 'type': None}
        else:
            return {'category': 'red', 'type': None}  # по умолчанию
    elif category_name in ['vodka', 'cognac', 'whiskey', 'tequila', 'rum', 'beer']:
        return {'category': category_name, 'type': None}
    elif category_name == 'other':
        type_val = subcategory_data.get('name')
        return {'category': 'other', 'type': type_val}
    else:
        return {'category': 'red', 'type': None}


def reconstruct_pairing(foods: List[Dict[str, str]]) -> tuple:
    """Восстанавливает строку pairing из списка еды."""
    names_en = [food.get('name', '') for food in foods if food.get('name')]
    names_ru = [food.get('name_ru', '') for food in foods if food.get('name_ru')]

    pairing_en = ', '.join(names_en)
    pairing_ru = ', '.join(names_ru)

    return pairing_en, pairing_ru


def reconstruct_varietal(varietals: List[Dict[str, Any]]) -> tuple:
    """Восстанавливает строку varietal из списка сортов."""
    parts_en = []
    parts_ru = []

    for varietal_data in varietals:
        var_data = varietal_data.get('varietal', {})
        name_en = var_data.get('name', '')
        name_ru = var_data.get('name_ru', '')
        percentage = varietal_data.get('percentage')

        if percentage is not None and percentage != 100.0:
            part_en = f"{name_en} {percentage}%"
            part_ru = f"\"{name_ru}\" {percentage}%" if name_ru else f"{name_en} {percentage}%"
        else:
            part_en = f"{name_en} 100%" if len(varietals) == 1 else name_en
            part_ru = f"\"{name_ru}\" 100%" if name_ru and len(varietals) == 1 else name_ru if name_ru else name_en

        if part_en.strip():
            parts_en.append(part_en)
        if part_ru.strip():
            parts_ru.append(part_ru)

    varietal_en = ', '.join(parts_en)
    varietal_ru = ', '.join(parts_ru)

    return varietal_en, varietal_ru


def test_conversion():
    """Тест конвертации: прямая и обратная, сравнение с исходными данными."""
    # Исходные данные
    original_data = {"-Lymluc5yKRoLQyYLbJG": {"category": "red", "count": 0, "country": "italy",
                                              "english": {"alc": "13.5%",
                                                          "description": "Intense, concentrated and deep ruby-colored, this wine offers elegant, complex aromas of red fruits. In the mouth it is rich and dense, but harmonious, with sweet, balanced tannins. \nThe wine has a long finish with a depth and structure that ensure its extraordinary longevity.",
                                                          "pairing": "Game (venison, birds), Lamb.", "region": "Tuscany, Bolgheri",
                                                          "subtitle": "Tenuta San Guido", "title": "Bolgheri Sassicaia 2014 DOC",
                                                          "varietal": "Cabernet Sauvignon 85%, Cabernet Franc 15%.", "vol": "0.75 l"},
                                              "imageTimestamp": 601582280.306055, "index": 6, "isHidden": True, "russian": {"alc": "13.5%",
                                                                                                                            "description": "Насыщенное, полнотелое вино, глубокого рубинового оттенка предлагает элегантные, сложные ароматы красных фруктов. Вино имеет богатый и плотный, но гармоничный вкус, со сладкими, сбалансированными танинами. \nОбладает послевкусием с глубиной и структурой, обеспечивающей его необычайную продолжительность.",
                                                                                                                            "pairing": "с дичью, бараниной.", "region": "Тоскана, Болгери", "subtitle": "Тенута Сан Гвидо",
                                                                                                                            "title": "Болгери Сассициана 2014 DOC",
                                                                                                                            "varietal": "\"каберне совиньон\" 85%, \"каберне фран\" 15%.", "vol": "0.75 l"},
                                              "uid": "-Lymluc5yKRoLQyYLbJG"}}

    # Конвертируем в словарь 2
    dict2 = convert_dict1_to_dict2(original_data)

    # Конвертируем обратно в словарь 1
    converted_back = convert_dict2_to_dict1(dict2)

    # Проверяем, что игнорируемые поля исключены
    expected_ignored = {'index', 'isHidden', 'uid', 'imageTimestamp'}

    success = True
    for key in original_data:
        original_entry = original_data[key]
        converted_entry = converted_back[key]

        # Проверяем, что игнорируемые поля не появились в конвертированном словаре
        for ignored_field in expected_ignored:
            if ignored_field in converted_entry:
                print(f"Ошибка: поле {ignored_field} не должно быть в конвертированном словаре")
                success = False

        # Проверяем, что остальные поля совпадают (без игнорируемых)
        for field in original_entry:
            if field not in expected_ignored:
                if field not in converted_entry:
                    print(f"Ошибка: поле {field} отсутствует в конвертированном словаре")
                    success = False
                    continue

                if field == 'english' or field == 'russian':
                    for subfield in original_entry[field]:
                        if subfield not in converted_entry[field]:
                            print(f"Ошибка: подполе {subfield} отсутствует в {field}")
                            success = False
                        elif original_entry[field][subfield] != converted_entry[field][subfield]:
                            print(
                                f"Ошибка: значение {field}.{subfield} не совпадает: {repr(original_entry[field][subfield])} != {repr(converted_entry[field][subfield])}"
                            )
                            success = False
                else:
                    if original_entry[field] != converted_entry[field]:
                        print(
                            f"Ошибка: значение поля {field} не совпадает: {repr(original_entry[field])} != {repr(converted_entry[field])}"
                        )
                        success = False

    if success:
        print("Тест пройден успешно: конвертация и обратная конвертация работают корректно")
    else:
        print("Тест не пройден: есть ошибки в конвертации")


# Запуск теста
if __name__ == "__main__":
    batch_convert_data('data.json')
