# app/core/utils/converters.py
import re
from typing import Dict, Any, List, Optional, Union


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
                            new_entry['vol'] = vol_num
                        elif eng_key == 'alc':
                            # Конвертируем alc
                            alc_str = str(eng_val).replace('%', '')
                            try:
                                alc_num = float(alc_str)
                            except ValueError:
                                alc_num = 0.0
                            drink['alc'] = alc_num
                        elif eng_key == 'region':
                            # Обработка региона
                            drink['subregion'] = parse_region(eng_val, russian_data.get('region', ''), country)
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
                        elif eng_key == 'age':
                            # age остается в drink как строка
                            drink['age'] = eng_val
                        else:
                            # Все остальные поля идут в drink
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
                        elif rus_key == 'age':
                            # age остается в drink как строка
                            drink['age_ru'] = rus_val
                        elif rus_key == 'alc':
                            # Конвертируем русский alc
                            alc_str = str(rus_val).replace('%', '')
                            try:
                                alc_num = float(alc_str)
                            except ValueError:
                                alc_num = 0.0
                            drink['alc_ru'] = alc_num
                        else:
                            # Все остальные русские поля идут в drink
                            drink[f"{rus_key}_ru"] = rus_val
                    
                    new_entry['drink'] = drink
                elif field == 'category':
                    # Устанавливаем category в основной словарь
                    new_entry['category'] = field_value
                elif field == 'count':
                    # Обработка count
                    new_entry['count'] = field_value if field_value is not None else None
                elif field == 'country':
                    # Обрабатываем страну в регионе
                    # Устанавливается в parse_region
                    pass
                elif field == 'uid':
                    # Используем UID для image_path
                    new_entry['image_path'] = f"{field_value}.png"
        
        # Устанавливаем vol в 0, если его нет
        if 'vol' not in new_entry:
            new_entry['vol'] = 0.0
        
        dict2[key] = new_entry
    
    return dict2


def parse_region(region_en: str, region_ru: str, country: str) -> Dict[str, Any]:
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
                    'country': {'name': capitalize_country_name(country), 'name_ru': None}}}


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
                perc_en = round(100.0 / len(varietals_en))
        
        # Очищаем названия сортов от процентов
        var_en_clean = re.sub(r'\s+\d+\.?\d*%$', '', var_en).strip()
        var_ru_clean = re.sub(r'\s+\d+\.?\d*%$', '', var_ru).strip() if var_ru else None
        
        # Капитализируем названия сортов
        var_en_clean = capitalize_varietal_name(var_en_clean)
        if var_ru_clean:
            var_ru_clean = capitalize_varietal_name_ru(var_ru_clean)
        
        result.append(
                {'varietal': {'name': var_en_clean, 'name_ru': var_ru_clean}, 'percentage': perc_en}
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
    # Учитываем кавычки перед названием сорта
    pattern = r'(["\']?)([^"\',%]+(?:\([^)]*\))?[^"\',%]*)\s*(\d+\.?\d*)%?'
    matches = re.findall(pattern, varietal_str)
    
    result = []
    for quote, name_part, percentage_str in matches:
        # Убираем лишние пробелы и кавычки
        name = name_part.strip()
        percentage = float(percentage_str) if percentage_str and percentage_str.strip() else None
        if name and not name.isspace():  # Добавляем только если есть название и оно не состоит из одних пробелов
            result.append((name, percentage))
    
    # Если не найдены подходящие паттерны, разделяем по запятым
    if not result:
        parts = re.split(r',', varietal_str)
        for part in parts:
            part = part.strip()
            if part and not part.isspace():
                # Проверяем, есть ли процент в этой части
                perc_match = re.search(r'(\d+\.?\d*)%$', part)
                if perc_match:
                    name_part = part[:perc_match.start()].strip()
                    name = name_part.strip()
                    percentage = float(perc_match.group(1))
                else:
                    name = part.strip()
                    percentage = None
                if name and not name.isspace():  # Добавляем только если есть название и оно не состоит из одних пробелов
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


def capitalize_varietal_name(name: str) -> str:
    """Приводит название сорта к нормальному виду."""
    # Разбиваем по пробелам и делаем заглавные буквы
    parts = name.split()
    return ' '.join([part.capitalize() for part in parts])


def capitalize_varietal_name_ru(name: str) -> str:
    """Приводит русское название сорта к нормальному виду."""
    # Просто возвращаем как есть, так как русские названия уже правильно форматированы
    return name


def get_russian_name(english_name: str) -> str:
    """Простое преобразование английского названия в русское."""
    translations = {'calvados': 'Кальвадос', 'sake': 'Cакэ', 'vodka': 'Водка', 'cognac': 'Коньяк', 'whiskey': 'Виски',
            'tequila': 'Текила', 'rum': 'Ром', 'beer': 'Пиво', 'red': 'Красное', 'white': 'Белое', 'rose': 'Розовое',
            'sparkling': 'Игристое', 'port': 'Портвейн'}
    return translations.get(english_name.lower(), None)


def test_direct_conversion():
    """Тест прямой конвертации."""
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
    
    # Выводим результат для проверки
    import json
    print("Результат прямой конвертации:")
    print(json.dumps(dict2, ensure_ascii = False, indent = 2))
    
    # Проверяем основные ожидаемые поля
    key = "-Lymluc5yKRoLQyYLbJG"
    entry = dict2[key]
    
    # Проверяем category
    assert entry.get('category') == 'red', f"category: ожидалось 'red', получено {entry.get('category')}"
    
    # Проверяем vol
    assert entry.get('vol') == 0.75, f"vol: ожидалось 0.75, получено {entry.get('vol')}"
    
    # Проверяем count
    assert entry.get('count') == 0, f"count: ожидалось 0, получено {entry.get('count')}"
    
    # Проверяем country в структуре
    drink = entry.get('drink', {})
    subregion = drink.get('subregion', {})
    region = subregion.get('region', {})
    country_info = region.get('country', {})
    country_name = country_info.get('name')
    assert country_name == 'Italy', f"country.name: ожидалось 'Italy', получено {country_name}"
    
    # Проверяем varietals
    varietals = drink.get('varietals', [])
    assert len(varietals) == 2, f"varietals: ожидалось 2 элемента, получено {len(varietals)}"
    
    # Первый сорт
    varietal1 = varietals[0]
    var_info1 = varietal1.get('varietal', {})
    name1 = var_info1.get('name')
    name_ru1 = var_info1.get('name_ru')
    percentage1 = varietal1.get('percentage')
    assert name1 == 'Cabernet Sauvignon', f"varietal[0].name: ожидалось 'Cabernet Sauvignon', получено {name1}"
    assert name_ru1 == 'Каберне Совиньон', f"varietal[0].name_ru: ожидалось 'Каберне Совиньон', получено {name_ru1}"
    assert percentage1 == 85.0, f"varietal[0].percentage: ожидалось 85.0, получено {percentage1}"
    
    # Второй сорт
    varietal2 = varietals[1]
    var_info2 = varietal2.get('varietal', {})
    name2 = var_info2.get('name')
    name_ru2 = var_info2.get('name_ru')
    percentage2 = varietal2.get('percentage')
    assert name2 == 'Cabernet Franc', f"varietal[1].name: ожидалось 'Cabernet Franc', получено {name2}"
    assert name_ru2 == 'Каберне Фран', f"varietal[1].name_ru: ожидалось 'Каберне Фран', получено {name_ru2}"
    assert percentage2 == 15.0, f"varietal[1].percentage: ожидалось 15.0, получено {percentage2}"
    
    print("Тест прямой конвертации пройден успешно!")


# Запуск теста
if __name__ == "__main__":
    test_direct_conversion()