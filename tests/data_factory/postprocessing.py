# tests/data_factory/postprocessing.py
import random
from faker import Faker

common_locales = [
    'ar', 'bg', 'bs', 'cs', 'da', 'de', 'el', 'en', 'es', 'et',
    'fa', 'fi', 'fr', 'he', 'hi', 'hr', 'hu', 'hy', 'id', 'it',
    'ja', 'ka', 'ko', 'lt', 'lv', 'mk', 'nl', 'no', 'pl', 'pt',
    'ro', 'ru', 'sk', 'sl', 'sv', 'th', 'tr', 'uk', 'zh'
]


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

    def fix_value(value, key: str = '_en'):
        if isinstance(value, bool):
            return value
        elif isinstance(value, int):
            if not (int_min <= value <= int_max):
                return random.randint(int_min, int_max)
        elif isinstance(value, float):
            if not (float_min <= value <= float_max):
                return random.uniform(float_min, float_max)
        elif isinstance(value, str):
            tmp = key.rsplit('_', 1)
            name = tmp[0]
            language = tmp[-1]
            language = language if language in common_locales else 'en'
            leng = 300 if name.startswith('description') else 25
            # return generate_simple_phrase(language, leng)
        return value

    def traverse(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    traverse(value)
                else:
                    fixed_value = fix_value(value, key)
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


def generate_simple_phrase(language='ru', target_length=100):
    """
    Упрощенная версия генератора фраз
    """
    fake = Faker(language)

    min_length = int(target_length * 0.85)
    max_length = int(target_length * 1.15)

    # Генерируем текст немного больше нужной длины
    phrase = fake.text(max_nb_chars=int(target_length * 1.2))

    # Если текст слишком короткий, добавляем еще
    while len(phrase) < min_length:
        phrase += " " + fake.sentence(nb_words=random.randint(3, 8))

    # Если текст слишком длинный, обрезаем до последнего полного предложения
    if len(phrase) > max_length:
        # Ищем точку или другой знак конца предложения
        cut_pos = max(phrase.rfind('.', 0, max_length),
                      phrase.rfind('!', 0, max_length),
                      phrase.rfind('?', 0, max_length))

        if cut_pos != -1:
            phrase = phrase[:cut_pos + 1]
        else:
            # Если не нашли знак конца, обрезаем до последнего пробела
            last_space = phrase.rfind(' ', 0, max_length - 3)
            if last_space != -1:
                phrase = phrase[:last_space].strip() + "."
    return phrase.strip()


ru_phrase = generate_simple_phrase('ru', 50)
#  print(f"Русская фраза ({len(ru_phrase)} символов): {ru_phrase}")

# Английский язык
en_phrase = generate_simple_phrase('en', 80)
# print(f"Английская фраза ({len(en_phrase)} символов): {en_phrase}")

# Французский язык
fr_phrase = generate_simple_phrase('fr', 120)
# print(f"Французская фраза ({len(fr_phrase)} символов): {fr_phrase}")
