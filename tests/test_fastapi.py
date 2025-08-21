# tests/test_fastapi.py

import pytest

pytestmark = pytest.mark.asyncio


async def test_fastapi_root(authenticated_client_with_db):
    """ тест подключения к url """
    ac = authenticated_client_with_db
    response = await ac.get('/')
    assert response.status_code == 200
    x = response.json()
    assert x == {"Hello": "World"}


async def test_swagger(authenticated_client_with_db):
    """ тест доступности  swagger """
    response = await authenticated_client_with_db.get('/docs')
    assert response.status_code == 200


async def test_redoc(authenticated_client_with_db):
    """ тест доступности redoc """
    response = await authenticated_client_with_db.get('/redoc')
    assert response.status_code == 200


@pytest.mark.skip
async def test_fault_fastapi_root(client):
    """ тест подключения к url """
    response = await client.get('/auth/token')
    assert response.status_code == 401, f'{response.status_code=}'
