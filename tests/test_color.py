# tests/test_color.py
import pytest
# from fastapi import status
# from tests.mocks.repository_mock import MockRepository
from httpx import AsyncClient, ASGITransport
from app.main import app

pytestmark = pytest.mark.asyncio


async def test_diagnostic_with_headers():
    """Тест с заголовками авторизации"""
    from app.auth.utils import create_access_token
    from app.auth.schemas import UserRead

    test_user = UserRead(
        id=1, username="test", email="admin@test.com", is_active=True, is_superuser=True,
        created_at="2023-01-01T00:00:00", password='test'
    )

    token = create_access_token({"sub": test_user.username, "user_id": test_user.id})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        client.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )

        response = await client.get("/drinks/")
        print(f"Drinks endpoint: {response.status_code}")
        print(f"Response: {response.text}")
        assert response.status_code == 200


async def test_debug_routing():
    """Тест для диагностики роутинга"""
    # Пробуем разные варианты URL
    from app.auth.utils import create_access_token
    from app.auth.schemas import UserRead

    test_user = UserRead(id=1, username="test", email="admin@test.com",
                         is_active=True, is_superuser=True,
                         created_at="2023-01-01T00:00:00", password='test')
    token = create_access_token({"sub": test_user.username, "user_id": test_user.id})

    async with AsyncClient(
            transport=ASGITransport(app=app),  # ✅ Обязательно!
            base_url="http://test"
    ) as client:
        client.headers.update({"Authorization": f"Bearer {token}",
                               "Accept": "application/json"})
        urls_to_test = ["/drinks", "/drinks/", "/drinks/1", "/drinks/1/"]

        for url in urls_to_test:
            response = await client.get(url)
            print(f"URL: {url} -> Status: {response.status_code}")
            if response.status_code == 307:
                print(f"  Redirect to: {response.headers.get('location')}")


async def test_diagnostic_simple():
    """Простой тест без фикстур для диагностики"""
    print("Testing ASGITransport...")

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as client:
            response = await client.get("/")
            print(f"✓ Success! Status: {response.status_code}")
            assert response.status_code in [200, 401, 404]

    except Exception as e:
        print(f"✗ Error: {e}")
        raise


async def test_get_drink_authenticated(async_client_with_token):
    """Тест получения напитков с аутентификацией"""
    # id = 1
    response = await async_client_with_token.get("/drinks/")
    print(f'{response=}')
    assert response.status_code == 200


async def test_async_client_with_token(async_client_with_token):
    response = await async_client_with_token.get('/login/')
    assert response.status_code == 200


async def test_swagger_redoc_with_token(async_client_with_token):
    # for x in ['/docs/', '/redoc/']:
    response = await async_client_with_token.get('/docs/')
    assert response.status_code == 200
