# tests/test_routers.py
"""
    тестируем все методы GET ( get all with pagination, get_one)
    новые методы добавляются автоматически
    добавить get_by_field
"""

import pytest
from app.core.schemas.base import ListResponse

pytestmark = pytest.mark.asyncio


async def test_get_all(authenticated_client_with_db, test_db_session, routers_get_all, fakedata_generator):
    """ тестирует методы get all - с проверкой формата ответа """
    routers = routers_get_all
    x = ListResponse.model_fields.keys()
    client = authenticated_client_with_db
    for prefix in routers:
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, 'метод GET для пути "{prefix}" возвращает некорректные данные'


async def test_get_one(authenticated_client_with_db, test_db_session,
                       routers_get_all, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    """
    tmp = [(a.path.lstrip('/').split('/')[0], a)
           for a in app.routes
           if all((isinstance(a, APIRoute), a.path not in ('/', '/auth/token', '/wait')))]
    for n, a in tmp:
        print(f'{n}: {a}')
    from collections import defaultdict
    result = defaultdict(set)
    for key, value in tmp:
        result[key].add(value)
    result = dict(result)

    assert False
    """
    x = ListResponse.model_fields.keys()
    for prefix in routers:
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, 'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        # assert False, tmp.keys()
        total = len(tmp['items'])
        if total > 0:
            id = 1  # randint(1, total)
            instance = tmp['items'][id - 1]
            resp = await client.get(f'{prefix}/{id}')
            assert resp.status_code == 200, f'{id} === {tmp}'
            result = resp.json()
            for key, val in instance.items():
                assert result.get(key) == val
        else:
            resp = await client.get(f'{prefix}/1')
            assert resp.status_code in [200, 404]
