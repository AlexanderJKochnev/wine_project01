# tests/test_category.py
import pytest
# from app.support.category.model import Category
# from app.support.category.schemas import CategoryCreate, CategoryRead
from app.support.category.router import CategoryRouter

pytestmark = pytest.mark.asyncio


async def test_category_create(authenticated_client_with_db, test_db_session):
    router = CategoryRouter()
    prefix = router.prefix
    print(prefix, '===============================')
    data = {'name': 'test_name'}
    client = authenticated_client_with_db
    headers = client.headers
    print(f'{headers=}')
    response = await client.post('/categories', data=data)
    assert response.status_code == 200
