# tests/test_category.py
import pytest
# from app.support.category.model import Category
# from app.support.category.schemas import CategoryCreate, CategoryRead
from app.support.category.router import CategoryRouter

pytestmark = pytest.mark.asyncio


async def test_category_create(authenticated_client_with_db, test_db_session):
    router = CategoryRouter()
    prefix = router.prefix
    data = {'name': 'test_name'}
    client = authenticated_client_with_db
    response = await client.post(f'{prefix}', json=data)
    assert response.status_code == 200
    result = response.json()
    for key, val in data.items():
        assert result.get(key) == val


async def test_category_get(authenticated_client_with_db, test_db_session):
    router = CategoryRouter()
    prefix = router.prefix
    client = authenticated_client_with_db
    response = await client.get(f'{prefix}')
    assert response.status_code == 200
    # result = response.json()
    """добавить проверку содержимого"""


async def test_category_get_one(authenticated_client_with_db, test_db_session):
    router = CategoryRouter()
    prefix = router.prefix
    client = authenticated_client_with_db
    params = {'id': 1}
    response = await client.get(f'{prefix}/one', params=params)  # ', params={'id': 16})
    assert response.status_code == 200, response
    result = response.json()
    for key, val in params.items():
        assert result.get(key) == val, result