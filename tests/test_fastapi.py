# tests/test_fastapi.py

import pytest

pytestmark = pytest.mark.asyncio


async def test_fastapi_root(async_test_app):
    """ тест подключения к url """
    ac, _ = async_test_app
    response = await ac.get('/')
    assert response.status_code == 200
    x = response.json()
    assert x == {"Hello": "World"}


async def test_sqladmin(async_test_app):
    """ тест доступности  sqladmin """
    ac, _ = async_test_app
    response = await ac.get('/admin/')
    assert response.status_code == 200


async def test_swagger(async_test_app):
    """ тест доступности  swagger """
    ac, _ = async_test_app
    response = await ac.get('/docs')
    assert response.status_code == 200


async def test_redoc(async_test_app):
    """ тест доступности redoc """
    ac, _ = async_test_app
    response = await ac.get('/redoc')
    assert response.status_code == 200
