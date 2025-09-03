# tests/test_search.py
"""
    тестируем все методы SEARCH
    новые методы добавляются автоматически
"""

import pytest
from typing import List
from app.core.schemas.base import ListResponse

pytestmark = pytest.mark.asyncio


async def test_search(authenticated_client_with_db, test_db_session,
                      routers_get_all, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    from random import randint
    client = authenticated_client_with_db
    routers = routers_get_all
    x = ListResponse.model_fields.keys()
    counter = 0
    for prefix in routers:          # перебирает существующие роутеры
        # if prefix == '/warehouses':
        #     continue
        response = await client.get(f'{prefix}')   # получает все записи (1 страница)
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, f'метод GET для пути "{prefix}" возвращает некорректные данные'

        tmp: List[dict] = response.json().get('items')
        tmp2: dict = {}
        for value in tmp:
            key = value.get('id')
            # формирует строку из слов из всех текстовых полей без повтров
            data = ' '.join({val.replace('.', ' ').
                            replace('  ', '^ ').
                            replace('^', '') for val in value.values()
                             if isinstance(val, str)}).split(' ')
            tmp2[key] = data
        try:
            bgstring = (val for val in tmp2.values())
            bgstring = set(sum(bgstring, []))
            bigstring = list(bgstring)
        except Exception as e:
            assert False, f'{tmp2}, {e}'

        query = bigstring[randint(0, len(bigstring) - 1)]
        # список id содержащий искомое слово
        expected_answer = [key for key, val in tmp2.items() if query in val]
        params = {'query': query}
        response = await client.get(f'{prefix}/search', params=params)
        assert response.status_code == 200, response.text
        result = response.json().get('items')
        answer = [item.get('id') for item in result]
        assert set(answer) == set(expected_answer), f'результат неверный {query} {prefix}'
        counter += 1
