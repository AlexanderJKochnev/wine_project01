# app.core.utils.ahocorassick.py
"""
     алгоритм поиска aho corasick
"""

import ahocorasick

# Глобальная переменная для хранения экстрактора
_extractor = None


def get_extractor(term_to_id=None):
    """
    """
    global _extractor
    if _extractor is None:  # <--- ЭТО ОДНА СТРОКА
        _extractor = build_extractor(term_to_id or {'run': 1, 'beautiful': 2, 'new york': 3})
    return _extractor


def build_extractor(term_to_id):
    """
        построение бора
    """
    auto = ahocorasick.Automaton()
    for term, tid in term_to_id.items():
        auto.add_word(term.lower(), tid)
    auto.make_automaton()
    return auto


def extract(text):
    return {term: tid for term, tid in get_extractor().iter(text.lower())}


def extract_batch(texts):
    return {tid: list(extract(t)) for tid, t in texts if extract(t)}


def update_dictionary(new_terms):
    global _extractor
    # Обновляем словарь и перестраиваем (для простоты — просто пересоздаем)
    current_dict = {'run': 1, 'beautiful': 2, 'new york': 3}  # загрузите актуальный
    current_dict.update(new_terms)
    _extractor = build_extractor(current_dict)


"""
Первый вызов — создает экстрактор (разогрев)
result = extract("New York is beautiful")  # {1, 2, 3}

# Второй вызов — использует существующий
result2 = extract("Run fast")  # {1}

# Batch-обработка
texts = [(101, "New York"), (102, "Run")]
results = extract_batch(texts)  # {101: [1, 2, 3], 102: [1]}
"""