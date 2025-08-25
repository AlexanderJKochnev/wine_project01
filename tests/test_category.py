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


async def test_category_get_one(authenticated_client_with_db, test_db_session):
    router = CategoryRouter()
    prefix = router.prefix
    client = authenticated_client_with_db
    data = {'name': 'test_name2'}
    response = await client.post(f'{prefix}', json=data)
    assert response.status_code == 200
    params = {'id': 1}
    response = await client.get(f'{prefix}/one', params=params)  # ', params={'id': 16})
    assert response.status_code == 200, response
    result = response.json()
    for key, val in params.items():
        assert result.get(key) == val, result

"""
async def fakedata_generator(authenticated_client_with_db, test_db_session, get_fields_type):
    client = authenticated_client_with_db
    counts = 10
    for key, val in get_fields_type.items():
        for n in range(counts):
            route = key
            if n % 2 == 1:
                data = {k2: v2() for k2, v2 in val['required_only'].items()}
            else:
                data = {k2: v2() for k2, v2 in val['all_fields'].items()}
            response = await client.post(f'{route}', json=data)
            assert response.status_code == 200, route
"""


async def test_category_get(authenticated_client_with_db, test_db_session, fakedata_generator):
    router = CategoryRouter()
    prefix = router.prefix
    client = authenticated_client_with_db
    response = await client.get(f'{prefix}')
    assert response.status_code == 200
    assert False, response.json()
    # result = response.json()
    """добавить проверку содержимого"""
