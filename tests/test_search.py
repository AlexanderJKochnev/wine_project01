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
    client = authenticated_client_with_db
    routers = routers_get_all
    x = ListResponse.model_fields.keys()
    counter = 0
    for prefix in routers:          # перебирает существующие роутеры
        response = await client.get(f'{prefix}')   # получает все записи (1 страница)
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, f'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        total = len(tmp['items'])
        if total > 0:
            instance = tmp['items'][-1]  # берем последнюю запись
            id = instance.get('id')
            dump: List[str] = []
            for key, val in instance.items():
                if isinstance(val, str) and key not in ['category', 'color', 'sweetness', 'region']:
                    dump.append(val)
            search_query = dump[-1].split(' ')[0]  # предпоследнее слово
            params = {'query': search_query}
            resp = await client.get(f'{prefix}/search', params=params)
            print("Status:", resp.status_code)
            print("Response body:", resp.json())  # или response.text
            assert resp.status_code == 200, (f'получение записи {prefix} c {id} неудачно {search_query=} '
                                             f'выполнено {counter} тестов успешно, '
                                             f'Expected 200, got {resp.status_code}, body: {resp.text}')
            result = resp.json()
            res = [instance for instance in result if instance.get('id') == id]
            assert res > 0, (f'поиск по слову {search_query} не удался в таблице {prefix}, '
                             f'выполнено {counter} тестов успешно')
        else:   # записей в тестируемой таблице нет, пропускаем
            print(f'{prefix} записей в тестируемой таблице нет, пропускаем')
        counter += 1
