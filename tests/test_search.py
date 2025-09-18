# tests/test_search.py
"""
    тестируем все методы SEARCH
    новые методы добавляются автоматически
"""

import pytest
from typing import List
from collections import Counter


pytestmark = pytest.mark.asyncio


def split_string(s: str, n: int = 3) -> List[str]:
    #  разбивает строку на список слов
    # return [s[i:i + n] for i in range(0, len(s), n)]
    return s.split(' ')


def count_and_sort_elements(input_list):
    """
    Преобразует список с повторяющимися элементами в список списков [элемент, количество],
    отсортированный по количеству повторов по убыванию.

    Args:
        input_list: список с повторяющимися элементами

    Returns:
        list: список списков формата [элемент, количество], отсортированный по количеству
    """
    # Считаем количество каждого элемента
    counter = Counter(input_list)

    # Сортируем элементы по количеству повторов (по убыванию)
    sorted_items = sorted(counter.items(), key=lambda x: x[1], reverse=True)

    # Преобразуем кортежи в списки
    result = [[item, count] for item, count in sorted_items]
    return result


def find_keys_by_word(data_dict: dict, search_word: str) -> list:
    """
    Находит ключи, значения которых содержат указанное слово.

    Args:
        data_dict: Словарь {key: value} где value - строки или None
        search_word: Слово для поиска

    Returns:
        List: Список ключей, содержащих слово в значениях
    """
    result = []
    search_word_lower = search_word.lower()
    for key, value in data_dict.items():
        if value is not None and search_word_lower in value.lower():
            result.append(key)

    return result


async def test_search(authenticated_client_with_db, test_db_session,
                      routers_get_all, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    # expected_response = PaginatedResponse.model_fields.keys()
    for prefix in routers:          # перебирает существующие роутеры
        response = await client.get(f'{prefix}/all')   # получает все записи
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        # assert response.json().keys() == expected_response, \
        #    f'метод GET для пути "{prefix}" возвращает некорректные данные'

        tmp: List[dict] = response.json()
        tmp2: list = []
        exp: dict = {}
        for value in tmp:
            """ список всех слов """
            id = value['id']
            data: list = ' '.join((val for val in value.values() if isinstance(val, str))).split(' ')
            exp[id] = ' '.join(data)
            tmp2.extend(data)
        tmp2 = count_and_sort_elements(tmp2)
        query, expected_nmbr = tmp2[0]
        expected_answer = find_keys_by_word(exp, query)
        params = {'query': query}

        response = await client.get(f'{prefix}/search', params=params)
        assert response.status_code == 200
        result = response.json()
        items = result.get('items')
        ids = [val['id'] for val in items]
        assert sorted(ids) == sorted(expected_answer), f'{ids=} {expected_answer=} {query=} {prefix=}'
