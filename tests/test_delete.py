# tests/test_delete.py
"""
    тестируем все методы POST и DELETE ()
    новые методы добавляются автоматически
    pytest tests/test_delete.py --tb=auto --disable-warnings -vv --capture=no
"""

import pytest

from app.core.schemas.base import PaginatedResponse

pytestmark = pytest.mark.asyncio


async def test_delete(authenticated_client_with_db, test_db_session,
                      routers_get_all, fakedata_generator):
    """ тестирует методы DELETE (update) - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    x = PaginatedResponse.model_fields.keys()
    for prefix in reversed(routers):
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, f'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        for key in tmp['items']:
            id = key['id']
            response = await client.delete(f'{prefix}/{id}')
            assert response.status_code == 200, response.text
            # gроверка удаления
            check = await client.get(f'{prefix}/{id}')
            assert check.status_code in [404, 500], check.text


@pytest.mark.skip
async def test_fault_delete(authenticated_client_with_db, test_db_session,
                            routers_get_all, fakedata_generator):
    """ тестирует методы DELETE (update) - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all
    for prefix in reversed(routers):
        id = 10000
        resp = await client.delete(f'{prefix}/{id}')
        assert resp.status_code == 404, resp.text


@pytest.mark.skip
async def test_delete_one_exact(authenticated_client_with_db, test_db_session,
                                simple_router_list, complex_router_list,
                                fakedata_generator):
    router_list = simple_router_list + complex_router_list
    # router_list = [ItemRouter, DrinkRouter]
    for item in router_list:
        router = item()
        prefix = router.prefix
        client = authenticated_client_with_db
        id = 1
        response = await client.delete(f'{prefix}/{id}')
        assert response.status_code == 200, f'{prefix}, {response.text}'
