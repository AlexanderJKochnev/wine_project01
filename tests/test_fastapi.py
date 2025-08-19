# tests/test_fastapi.py

import pytest

pytestmark = pytest.mark.asyncio


async def test_fastapi_root(authenticated_client):
    """ тест подключения к url """
    ac = authenticated_client
    response = await ac.get('/')
    assert response.status_code == 200
    x = response.json()
    assert x == {"Hello": "World"}


async def test_swagger(authenticated_client):
    """ тест доступности  swagger """
    ac = authenticated_client
    response = await ac.get('/docs')
    assert response.status_code == 200


async def test_redoc(authenticated_client):
    """ тест доступности redoc """
    ac = authenticated_client
    response = await ac.get('/redoc')
    assert response.status_code == 200


async def test_fault_fastapi_root(unauthenticated_client):
    """ тест подключения к url """
    client = unauthenticated_client
    response = await client.get('/')
    assert response.status_code == 401
