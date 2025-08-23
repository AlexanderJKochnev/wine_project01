# tests/test_category.py
import pytest
from app.core.schemas.base import ListResponse
pytestmark = pytest.mark.asyncio


async def test_get_all(authenticated_client_with_db, test_db_session, routers_get_all):
    """ тестирует методы get all - с проверкой формата ответа """
    routers = routers_get_all
    x = ListResponse.model_fields.keys()
    client = authenticated_client_with_db
    for prefix in routers:
        response = await client.get(f'{prefix}')
        assert response.status_code == 200, 'метод GET не работает для пути "{prefix}"'
        assert response.json().keys() == x, 'метод GET для пути "{prefix}" возвращает некорректные данные'


async def test_get_one(authenticated_client_with_db, test_db_session, routers_get_one):
    """ тестирует методы get one - без проверки содержимого """
    routers = routers_get_one
    client = authenticated_client_with_db
    params = {'id': 1}
    for prefix in routers:
        response = await client.get(f'{prefix}1/one', params=params)
        assert response.status_code in [200, 404]
