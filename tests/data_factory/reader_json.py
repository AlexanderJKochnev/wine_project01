# tests/data_factory/reader.json
import json
import copy
from pathlib import Path
import re
from typing import List, Tuple, Union, Optional, Dict


def jprint(data: dict):
    print(json.dumps(data, indent=2, ensure_ascii=False))


class JsonConverter():
    def __init__(self, filename: str = 'data.json', input_dir: str = 'input'):
        self.languages: dict = {'english': '',
                                'russian': '_ru',
                                'francaise': '_fr'}
        self.sinle_lang: list = ['age', 'alc', 'vol']
        self.exclude_list: list = ['index', 'isHidden',
                                   'uid', 'imageTimestamp',
                                   'count']
        self.data: dict = self.json_reader(filename, input_dir)
        self.json_preprocessing()
        self.json_list(self.data)  # преобразует в плоский словарь
        self.fields_list = self.get_key_values(self.data)
        self.json_postpocessing()

    def __call__(self, *args, **kwargs):
        # print(self.get_keys(self.data))
        # jprint(self.data)
        return self.data

    def transform_pairings(self, data):
        result = {"name": data["name"], "foods": []}

        pairing_en = data.get("pairing", [])
        pairing_ru = data.get("pairing_ru", [])

        # Объединяем списки попарно
        for en, ru in zip(pairing_en, pairing_ru):
            result["foods"].append(
                {"name": en, "name_ru": ru}
            )
        return result

    def is_hashable(self, obj):
        try:
            hash(obj)
            return True
        except TypeError:
            return False

    def camelcase(self, input) -> str:
        if input:
            input = input.replace('_', ' ')
            return ' '.join((a.title() for a in input.split(' ')))
        else:
            return input

    def extract_float_advanced(self, text):
        """Продвинутое извлечение чисел с разными форматами"""
        # Поддерживает: 123.45, -42.5, 1,234.56, 1.234,56 (европейский формат)
        patterns = [r'-?\d{1,3}(?:,\d{3})*\.\d+',  # 1,234.56
                    r'-?\d{1,3}(?:\.\d{3})*,\d+',  # 1.234,56 (европейский)
                    r'-?\d+\.\d+',  # 123.45
                    r'-?\d+'  # 123
                    ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                number_str = match.group()
                # Заменяем запятые на точки для европейского формата
                if ',' in number_str and '.' in number_str:
                    number_str = number_str.replace('.', '').replace(',', '.')
                elif ',' in number_str and number_str.count(',') == 1:
                    # Если одна запятая, возможно это десятичный разделитель
                    number_str = number_str.replace(',', '.')
                try:
                    return float(number_str)
                except ValueError:
                    continue

        return None

    def robust_string_to_list(self, input_string: str) -> List[str]:
        """
        Надежная версия обработки строки в список (pairing)
        """
        if not input_string or not input_string.strip():
            return tuple()

        # Удаляем лишние пробелы
        input_string = input_string.strip()

        # Обрабатываем множественные запятые
        input_string = re.sub(r',+', ',', input_string)

        # Временное хранилище для скобочных конструкций
        protected = {}

        # Заменяем запятые внутри скобок на специальный маркер
        def protect_commas(match):
            protected_id = f'@@@PROTECTED_{len(protected)}@@@'
            protected[protected_id] = match.group(0)
            return protected_id

        # Маскируем содержимое скобок
        protected_string = re.sub(r'\([^)]+\)', protect_commas, input_string)

        # Разделяем по запятым
        parts = [part.strip() for part in protected_string.split(',')
                 if part.strip()]

        # Восстанавливаем скобочные конструкции
        result = []
        for part in parts:
            for protected_id, original in protected.items():
                part = part.replace(protected_id, original)

            # Убираем точки в конце
            part = re.sub(r'\.+$', '', part)

            # Приводим к правильному регистру
            if part:
                part = part[0].upper() + part[1:].lower() \
                    if part[0].isalpha() else part

            result.append(part)

        return tuple(result)

    def parse_varietal_string_clean(
            self, varietal_str: str,
            key_name: str = 'varietal') -> List[Dict[str, Optional[float]]]:
        """
        Версия с максимальной очисткой специальных символов.
        """
        # Удаляем все не-ASCII символы кроме букв, цифр и пробелов
        cleaned_str = re.sub(r'[^\w\s\d%,.-]', '', varietal_str.strip())
        cleaned_str = re.sub(r'\.$', '', cleaned_str)

        if not cleaned_str:
            return []

        # Разделяем по запятым
        parts = [part.strip() for part in cleaned_str.split(',')
                 if part.strip()]

        result = []
        total_percentage = 0
        components_without_percentage = []

        for part in parts:
            # Ищем процент в конце
            percentage_match = re.search(r'(\d+(?:\.\d+)?)\s*%$', part)

            if percentage_match:
                percentage = float(percentage_match.group(1))
                varietal_name = re.sub(r'\s*\d+(?:\.\d+)?\s*%$',
                                       '', part).strip()
                total_percentage += percentage
            else:
                percentage = None
                varietal_name = part.strip()

            # Обработка диапазонов
            if ' to ' in varietal_name or '-' in varietal_name:
                range_match = re.search(r'(\d+)\s*(?:to|-)\s*(\d+)',
                                        varietal_name)
                if range_match:
                    min_val = float(range_match.group(1))
                    max_val = float(range_match.group(2))
                    percentage = (min_val + max_val) / 2
                    varietal_name = re.sub(r'\s*\d+\s*(?:to|-)\s*\d+\s*%?',
                                           '', varietal_name).strip()

            # Финальная очистка названия
            varietal_name = re.sub(r'^\s+|\s+$', '', varietal_name)

            if not varietal_name:
                continue

            if percentage is None:
                components_without_percentage.append(varietal_name)
            else:
                result.append(
                    {key_name: varietal_name, 'percentage': percentage}
                )

        # Обработка компонентов без процентов
        if components_without_percentage:
            if total_percentage < 100 and components_without_percentage:
                remaining_percentage = 100 - total_percentage
                per_component = (remaining_percentage /
                                 len(components_without_percentage))

                for varietal_name in components_without_percentage:
                    result.append(
                        {key_name: varietal_name,
                         'percentage': per_component}
                    )
            else:
                for varietal_name in components_without_percentage:
                    result.append(
                        {key_name: varietal_name, 'percentage': None}
                    )

        # Если один элемент без процента - 100%
        if len(result) == 1 and result[0]['percentage'] is None:
            result[0]['percentage'] = 100.0

        return result

    def json_reader(self, filename: str, input_dir: str) -> dict:
        """ читает json file """
        try:
            source = Path(__file__).resolve().parent.joinpath(filename)
            if source.exists():
                with open(source) as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    return self.input_validate(data)
        except Exception as e:
            print(f'Json_reader error: {e}')
            return None

    def input_validate(self, data: dict) -> dict:
        """ валидирует полученный словарь"""
        if isinstance(data, dict):
            result = data.get('items')
            if all((result, isinstance(result, dict))):
                return result
        return None

    def json_list(self, data: dict) -> dict:
        """ проходит по верхнему уровню словаря """
        try:
            for key, val in data.items():
                data[key] = self.json_flattern(val)
            return True
        except Exception as e:
            print(f'json_list.error: {e}')
            return False

    def json_flattern(self, data: dict, lang: str = '') -> dict:
        """ превращает словарь в плоский """
        result: dict = {}
        for key, val in data.items():
            if isinstance(val, dict):
                lang = self.languages.get(key, '')
                result.update(self.json_flattern(val, lang))
            else:
                result[f'{key}{lang}'] = val
        return result

    def get_keys(self, data: dict) -> list:
        """ список ключей """
        return sorted(list(set(sum((list(val.keys())
                                    for key, val in data.items()), []))))

    def pretty_print(self, data: dict):
        return json.dumps(data, indent=2, ensure_ascii=False)

    def get_summary(self, flat_data: dict) -> dict:
        result = {key: val for key, val in flat_data.items()}
        return result

    def json_preprocessing(self) -> dict:
        for key, val in self.data.items():
            for item in self.sinle_lang:
                val['russian'].pop(item, None)
            for item in self.exclude_list:
                val['russian'].pop(item, None)
                val['english'].pop(item, None)
                val.pop(item, None)

    def get_key_values(self, data1: dict) -> dict:
        result: dict = {}
        data = copy.deepcopy(data1)
        for key, val in data.items():
            self.data[key]['image_path'] = key
            if isinstance(val, dict):
                for k2, v2 in val.items():
                    if k2 in ['type', 'type_ru']:
                        k2 = k2.replace('type', 'subcaterory')
                    if v2:
                        """ """
                        v2 = self.field_processing(k2, v2)
                        if k2 in ['region', 'region_ru']:
                            if ',' in v2:
                                region, subregion = v2.split(',', 1)
                                self.data[key][k2] = region.strip()
                                self.data[key][f'sub{k2}'] = subregion.strip()
                            else:
                                self.data[key][k2] = v2
                        else:
                            self.data[key][k2] = v2  # !
                        try:
                            if result.get(k2):
                                tmp = result.get(k2)
                            else:
                                tmp = []
                            if isinstance(v2, Union[List, Tuple]):
                                tmp.extend(v2)
                            elif isinstance(v2, dict):
                                tmp.extend(list(v2.keys()))
                            else:
                                tmp.append(v2)
                            result[k2] = tmp
                        except Exception as e:
                            print(f'========================{e}')
        result = {key: list(set(val)) for key, val in result.items()
                  if self.is_hashable(val)}
        return result

    def field_processing(self, key: str, val: str):
        """Преобразование значений"""
        match key:
            case 'alc':
                result = self.extract_float_advanced(val)
            case 'pairing':
                result = self.robust_string_to_list(val)
                # result = tuple(v1.strip('.').rstrip(' ')
                #                for v1 in val.split(','))
            case 'pairing_ru':
                result = self.robust_string_to_list(val)
                # result = tuple(v1.strip('.').rstrip(' ')
                #                for v1 in val.split(','))
            case 'vol':
                result = float(val.rstrip(' l'))
            case 'varietal':
                result = self.parse_varietal_string_clean(val, 'name')
            case 'varietal_ru':
                result = self.parse_varietal_string_clean(val, 'name_ru')
            case _:
                result = val
        return result

    def json_postpocessing(self):
        data = copy.deepcopy(self.data)
        category: dict = {}
        subregion: dict = {}
        country: dict = {}
        region: dict = {}
        subcategory = {}
        """
        pairing_en = []
        pairing_ru = []
        foods = []
        varietals_en = []
        varietals_ru = []
        varietals = []"""
        for key, val in data.items():
            subregion['name'] = self.camelcase(
                self.data[key].pop('subregion', ''))
            subregion['name_ru'] = self.camelcase(
                self.data[key].pop('subregion_ru', None))
            region['name'] = self.camelcase(
                self.data[key].pop('region', ''))
            region['name_ru'] = self.camelcase(
                self.data[key].pop('region_ru', None))
            country['name'] = self.camelcase(
                self.data[key].pop('country', ''))
            country['name_ru'] = self.camelcase(
                self.data[key].pop('country_ru', None))
            region['country'] = country
            subregion['region'] = region
            self.data[key]['subregion'] = subregion

            subcategory['name'] = self.camelcase(
                self.data[key].pop('subcategory', ''))
            subcategory['name_ru'] = self.camelcase(
                self.data[key].pop('subcategory_ru', None))
            category['name'] = self.camelcase(
                self.data[key].pop('category', ''))
            category['name_ru'] = self.camelcase(
                self.data[key].pop('category_ru', None))
            subcategory['category'] = category
            self.data[key]['subcategory'] = subcategory
            # pairing -> foods
            pairing_en = self.data[key].pop("pairing", [])
            pairing_ru = self.data[key].pop("pairing_ru", [])
            foods = []
            for en, ru in zip(pairing_en, pairing_ru):
                foods.append({"name": en, "name_ru": ru})
            if foods:
                self.data[key]['foods'] = foods
            # varietals
            varietals = []
            varietals_en = data[key].pop("varietal", [])
            varietals_ru = data[key].pop("varietal_ru", [])

            # Проверим, что списки одной длины
            if len(varietals_en) != len(varietals_ru):
                raise ValueError("Списки 'varietal' и 'varietal_ru' "
                                 "должны быть одинаковой длины")

            for item_en, item_ru in zip(varietals_en, varietals_ru):
                # Проверка: проценты должны совпадать (по смыслу)
                # if item_en["percentage"] != item_ru["percentage"]:
                #     raise ValueError(f"Проценты не совпадают: "
                #                      f"{item_en} vs {item_ru}")

                merged_item = {"varietal": {"name": self.camelcase(item_en["name"]),
                                            "name_ru": self.camelcase(item_ru["name_ru"])},
                               "percentage": item_en.get("percentage")}
                varietals.append(merged_item)
            if varietals:
                self.data[key]['varietals'] = varietals
            category: dict = {}
            subregion: dict = {}
            country: dict = {}
            region: dict = {}
            subcategory = {}


if __name__ == '__main__':
    result = JsonConverter()
    print(result())
