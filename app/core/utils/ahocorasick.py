# app.core.utils.ahocorassick.py
"""
     алгоритм поиска aho corasick
"""
import asyncio
import ahocorasick
from sqlalchemy.ext.asyncio import AsyncSession

# Глобальные хранилища для боров и блокировка от состояния гонки
_extractors = {}
_lock = asyncio.Lock()


async def get_extractor(task_type: str,
                        session: AsyncSession,
                        db_filter: dict,
                        translatehelpservice) -> ahocorasick.Automaton:
    """
    Ленивая инициализация нужного бора. При первом вызове загружает данные из БД.
    """
    global _extractors

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


def get_translations_with_aho(text: str, auto: ahocorasick.Automaton) -> dict:
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


async def refresh_extractor(task_type: str, session: AsyncSession, db_filter: dict, dataclass) -> None:
    """
    Принудительное обновление конкретного бора.
    Загружает актуальные данные из БД и атомарно заменяет старый бор в памяти.
    """
    global _extractors

    async with _lock:
        # 1. Загружаем свежие данные из базы данных
        term_to_data = await dataclass.get_dict(session, db_filter)

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
