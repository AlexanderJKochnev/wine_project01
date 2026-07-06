# app.core.utils.ahocorassick.py
"""
     алгоритм поиска aho corasick
"""
import asyncio
import ahocorasick
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.pydantic_utils import get_service

# Глобальные хранилища для боров и блокировка от состояния гонки
_extractors = {}
_lock = asyncio.Lock()


async def get_extractor(task_type: str,
                        session: AsyncSession,
                        db_filter: dict) -> ahocorasick.Automaton:
    """
    Ленивая инициализация нужного бора. При первом вызове загружает данные из БД.
    """
    global _extractors
    translatehelpservice = get_service('TranslateHelper')
    if task_type not in _extractors:
        async with _lock:
            # Double-check под блокировкой для безопасного асинхронного доступа
            if task_type not in _extractors:
                term_to_data = await translatehelpservice.get_dict(session, db_filter)

                auto = ahocorasick.Automaton()
                if term_to_data:
                    for term, val in term_to_data.items():
                        # Ключ всегда приводим к нижнему регистру для регистронезависимого поиска.
                        # В значение сохраняем кортеж (длина_ключа, целевое_значение).
                        auto.add_word(term.lower(), (len(term), val))

                auto.make_automaton()
                _extractors[task_type] = auto

    return _extractors[task_type]


def clean_text_with_aho(text: str, auto: ahocorasick.Automaton) -> str:
    """
    Заменяет мусорные подстроки. Работает через индексы за один проход,
    не ломает индексы при изменении длины строки и сохраняет регистр полезного текста.
    """
    if not text:
        return text

    lower_text = text.lower()
    matches = []

    # Сбор всех совпадений мусора
    for end_idx, (word_len, replacement) in auto.iter(lower_text):
        start_idx = end_idx - word_len + 1
        matches.append((start_idx, end_idx + 1, replacement))

    if not matches:
        return text

    # Сортируем совпадения по позиции начала
    matches.sort(key=lambda x: x[0])

    result = []
    last_idx = 0

    for start, end, replacement in matches:
        # Исключаем перекрывающиеся или вложенные совпадения
        if start < last_idx:
            continue
        # Добавляем чистый кусок текста ДО мусора
        result.append(text[last_idx:start])
        # Добавляем замену (например, пустую строку или пробел)
        result.append(replacement)
        last_idx = end

    # Добавляем оставшийся хвост строки
    result.append(text[last_idx:])
    return "".join(result)


def get_translations_with_aho_old(text: str, auto: ahocorasick.Automaton) -> dict:
    """
    Находит все совпадения для подсказок перевода.
    Возвращает словарь {слово_из_текста: set_вариантов} с сохранением регистра ключа.
    """
    if not text:
        return {}

    lower_text = text.lower()
    hints = {}

    for end_idx, (word_len, translation_data) in auto.iter(lower_text):
        start_idx = end_idx - word_len + 1
        # Извлекаем оригинальное написание слова из исходного текста
        original_word = text[start_idx: end_idx + 1]

        # Гарантируем, что на выходе будет set, даже если в БД лежит одиночная строка
        if isinstance(translation_data, (set, list)):
            hints[original_word] = set(translation_data)
        else:
            hints[original_word] = {str(translation_data)}

    return hints


def get_translations_with_aho(text: str, auto: ahocorasick.Automaton) -> dict:
    """
    Находит все совпадения для подсказок перевода.
    Исключает вложенные короткие слова с помощью линейного массива занятых индексов.
    """
    if not text:
        return {}

    lower_text = text.lower()
    all_matches = []

    # Шаг 1: Собираем все возможные совпадения
    for end_idx, (word_len, translation_data) in auto.iter(lower_text):
        start_idx = end_idx - word_len + 1
        all_matches.append(
            {'start': start_idx, 'end': end_idx, 'len': word_len, 'data': translation_data}
        )

    # Шаг 2: Сортируем от самых длинных к коротким
    all_matches.sort(key=lambda x: (-x['len'], x['start']))

    # Шаг 3: Массив флагов для отслеживания занятых символов текста
    # Длина равна длине текста, изначально все символы свободны (False)
    occupied = [False] * len(text)

    hints = {}

    for match in all_matches:
        start, end = match['start'], match['end']

        # Проверяем, свободен ли ХОТЯ БЫ ОДИН символ для этого слова.
        # Если слово ПОЛНОСТЬЮ внутри уже занятого отрезка, any() вернет True,
        # и мы инвертируем это в False (пропускаем).
        # Если это пересечение краями (что редко для токенов слов), мы его тоже не берем.
        if any(occupied[start:end + 1]):
            continue

        # Отмечаем символы этого совпадения как занятые
        for i in range(start, end + 1):
            occupied[i] = True

        # Шаг 4: Формируем финальный словарь подсказок
        original_word = text[start: end + 1]
        translation_data = match['data']

        if isinstance(translation_data, (set, list)):
            current_set = set(translation_data)
        else:
            current_set = {str(translation_data)}

        if original_word in hints:
            hints[original_word].update(current_set)
        else:
            hints[original_word] = current_set

    return hints


async def refresh_extractor(task_type: str, session: AsyncSession, db_filter: dict) -> None:
    """
    Принудительное обновление конкретного бора.
    Загружает актуальные данные из БД и атомарно заменяет старый бор в памяти.
    """
    global _extractors
    translatehelpservice = get_service('TranslateHelper')
    async with _lock:
        # 1. Загружаем свежие данные из базы данных
        term_to_data = await translatehelpservice.get_dict(session, db_filter)

        # 2. Строим новый автомат во временную переменную.
        # Пока идет этот процесс, ваши циклы продолжают читать старый бор без сбоев.
        new_auto = ahocorasick.Automaton()
        if term_to_data:
            for term, val in term_to_data.items():
                if task_type == 'cleaner':
                    if isinstance(val, (list, set, tuple)):
                        val = str(next(iter(val))) if val else ""
                    else:
                        val = str(val)

                new_auto.add_word(term.lower(), (len(term), val))

        new_auto.make_automaton()

        # 3. Атомарно подменяем ссылку в глобальном словаре
        _extractors[task_type] = new_auto


def get_loaded_extractor_tasks() -> list[str]:
    """
    Возвращает список всех task_type (ключей),
    которые сейчас загружены и активны в памяти приложения.
    """
    global _extractors
    return list(_extractors.keys())
