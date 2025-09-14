# tests/test_search.py
"""
    тестируем все методы SEARCH
    новые методы добавляются автоматически
"""

import pytest
from typing import List
from collections import Counter

from app.core.schemas.base import PaginatedResponse

pytestmark = pytest.mark.asyncio


def split_string(s: str, n: int = 3) -> List[str]:
    return [s[i:i + n] for i in range(0, len(s), n)]


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


async def test_search(authenticated_client_with_db, test_db_session,
                      routers_get_all, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    x = PaginatedResponse.model_fields.keys()
    for prefix in routers:          # перебирает существующие роутеры
        response = await client.get(f'{prefix}')   # получает все записи (1 страница)
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, f'метод GET для пути "{prefix}" возвращает некорректные данные'

        tmp: List[dict] = response.json().get('items')
        tmp2: list = []
        for value in tmp:
            data = ' '.join((' '.join(split_string(val, 3))
                             for val in value.values() if isinstance(val, str))).split(' ')
            tmp2.extend(data)
        tmp2 = count_and_sort_elements(tmp2)
        query, expected_nmbr = tmp2[0]
        # expected_answer = [key for key, val in tmp2.items() if query in val]
        params = {'query': query}

        response = await client.get(f'{prefix}/search', params=params)
        assert response.status_code == 200
        result = response.json()
        nmbr = result.get('total')
        assert nmbr >= expected_nmbr, f'{nmbr=} {expected_nmbr=}'
