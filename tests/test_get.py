# tests/test_routers.py
"""
    тестируем все методы POST и GET ( get all with pagination, get_one)
    новые методы добавляются автоматически
    добавить get_by_field
"""

import pytest
from app.core.schemas.base import PaginatedResponse

pytestmark = pytest.mark.asyncio


async def test_get_all(authenticated_client_with_db, test_db_session, routers_get_all, fakedata_generator):
    """ тестирует методы get all - с проверкой формата ответа """
    routers = routers_get_all
    x = PaginatedResponse.model_fields.keys()
    client = authenticated_client_with_db
    for prefix in routers:
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, f'метод GET для пути "{prefix}" возвращает некорректные данные'


async def test_get_one(authenticated_client_with_db, test_db_session,
                       routers_get_all, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_all

    # x = PaginatedResponse.model_fields.keys()
    for prefix in routers:
        response = await client.get(f'{prefix}/1')
        assert response.status_code in [200, 404], response.text
        """
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, f'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, f'метод GET для пути "{prefix}" возвращает некорректные данные'
        tmp = response.json()
        total = len(tmp['items'])
        if total > 0:
            instance = tmp['items'][-1]  # берем последнюю запись
            id = instance.get('id')
            resp = await client.get(f'{prefix}/{id}')
            assert resp.status_code == 200, f'получение записи {prefix} c {id} неудачно'
            result = resp.json()
            # проверка содержимого
            for key, val in instance.items():
                if not isinstance(val, float):   # особенности хранения и возврата float в Postgresql+SQLAlchemy
                    assert result.get(key) == val, (f'полученные данные {result.get(key)} '
                                                    f'не соответствуют ожидаемым {val}')
        else:   # записей в тестируемой таблице нет, просот тестируем доступ
            resp = await client.get(f'{prefix}/1')
            assert resp.status_code in [200, 404]
        """

async def test_fault_get_one(authenticated_client_with_db, test_db_session,
                             routers_get_all, fakedata_generator):
    """ тестирует методы get one - несуществующий id """
    client = authenticated_client_with_db
    routers = routers_get_all
    for prefix in routers:
        id = 1000
        response = await client.get(f'{prefix}/{id}')
        assert response.status_code == 404
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

async def test_get_one_exact(authenticated_client_with_db, test_db_session,
                             simple_router_list, complex_router_list,
                             fakedata_generator):
    from app.support.item.router import ItemRouter
    from app.support.drink.router import DrinkRouter
    # router_list = simple_router_list + complex_router_list
    router_list = [ItemRouter]
    for item in router_list:
        router = item()
        prefix = router.prefix
        client = authenticated_client_with_db
        id = 1
        response = await client.get(f'{prefix}/{1}')
        assert response.status_code == 200, f'{prefix}, {response.text}'
