# tests/test_routers.py
"""
    тестируем все методы GET ( get all with pagination)
    новые методы добавляются автоматически
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
                       routers_get_all, routers_get_one, fakedata_generator):
    """ тестирует методы get one - c проверкой id """
    client = authenticated_client_with_db
    routers = routers_get_one
    params = {'id': 1}
    for prefix in routers:
        response = await client.get(f'{prefix}1/one', params=params)
        assert response.status_code in [200, 404]
