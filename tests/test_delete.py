# tests/test_delete.py
"""
    тестируем все методы POST и DELETE ()
    новые методы добавляются автоматически
    pytest tests/test_delete.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest
from app.core.schemas.base import ListResponse

pytestmark = pytest.mark.asyncio


async def test_delete(authenticated_client_with_db, test_db_session,
                      routers_get_all, fakedata_generator):
    """ тестирует методы DELETE (update) - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    x = ListResponse.model_fields.keys()
    for prefix in reversed(routers):
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, 'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        total = len(tmp['items'])
        if total > 0:       # записи есть
            id = 2  # берем вторую
            instance = tmp['items'][id - 1]
            try:
                resp = await client.delete(f'{prefix}/{id}')
                assert resp.status_code == 200, f'{instance} // {resp}'
            except Exception as e:
                assert False, f'ошибка {e}, {instance}'

            # проверка удаления
            resp = await client.get(f'{prefix}/{id}')
            assert resp.status_code == 404, instance
        else:
            assert False, 'генератор тестовых данных не сработал на {prefix}. см. test_routers.py'


async def test_fault_delete(authenticated_client_with_db, test_db_session,
                            routers_get_all, fakedata_generator):
    """ тестирует методы DELETE (update) - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    for prefix in reversed(routers):
        id = 10000
        resp = await client.delete(f'{prefix}/{id}')
        assert resp.status_code == 404, resp
