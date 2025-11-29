# tests/test_auth.py
import pytest

pytestmark = pytest.mark.asyncio
""" тесты на создание пользователей и доступ к защищенным роутерам"""


async def test_create_user(authenticated_client_with_db):
    """Тест создания пользователя"""
    user_data = {"username": "newuser", "email": "newuser@example.com",
                 "password": "newpassword123"}
    client = authenticated_client_with_db
    response = await client.post("/users", json=user_data)
    print(f"Create user response: {response.status_code} - {response.text}")
    # Проверяем успешное создание
    assert response.status_code in [200, 201], f"Expected 200 or 201, got {response.status_code}"
    if response.status_code in [200, 201]:
        data = response.json()
        assert data["username"] == user_data["username"]
        assert "hashed_password" not in data


async def test_login_success(authenticated_client_with_db, super_user_data):
    """Тест успешной авторизации"""
    # login_client уже должен быть авторизован
    # Проверяем, что у клиента есть токен
    login_client = authenticated_client_with_db
    assert hasattr(login_client, '_access_token')
    assert login_client._access_token is not None
    # Пробуем получить информацию о пользователе
    response = await login_client.get("/users/me")
    assert response.status_code == 200
    result = response.json()
    assert result.get('username') == super_user_data.get('username'), result


async def test_login_failure(client):
    """Тест неудачной авторизации"""
    login_data = {"username": "nonexistent", "password": "wrongpassword"}
    response = await client.post("/auth/token", data=login_data)
    print(f"Login failure response: {response.status_code} - {response.text}")

    # Должно быть 401 (unauthorized)
    assert response.status_code == 401


async def test_get_current_user_unauthenticated(client):
    """Тест получения информации о пользователе без авторизации"""
    #  для внутрисетевых запросов авторизация не требуется, но и запрос без токена в шапке должен проходить без ошибки
    response = await client.get("/users/me")
    print(f"Unauthenticated get user me response: {response.status_code} - {response.text}")
    # Должно быть 401 (unauthorized)
    assert response.status_code == 401, response.text

"""Тесты для endpoints пользователей"""


async def test_get_user_me_authenticated(authenticated_client_with_db):
    """Тест получения информации о себе"""
    response = await authenticated_client_with_db.get("/users/me")
    print(f"Get user me response: {response.status_code} - {response.text}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == authenticated_client_with_db._test_user["username"]


async def test_get_user_me_unauthenticated(client):
    """Тест получения информации о себе без авторизации"""
    response = await client.get("/users/me")
    print(f"Unauthenticated get user me response: {response.status_code} - {response.text}")

    # Должно быть 401 (unauthorized)
    assert response.status_code == 401
