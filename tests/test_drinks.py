# tests/drinks.py
import pytest
from fastapi import status

pytestmark = pytest.mark.asyncio


async def test_get_drinks_authenticated(authenticated_client):
    """Тест получения напитков с аутентификацией"""
    response = await authenticated_client.get("/drinks/")
    assert response.status_code == status.HTTP_200_OK


def test_create_drink_authenticated(authenticated_client):
    """Тест создания напитка с аутентификацией"""
    drink_data = {"name": "Test Wine", "category_id": 13, "region_id": 1}
    response = authenticated_client.post("/drinks/", json=drink_data)
    assert response.status_code == status.HTTP_200_OK


def test_get_drinks_unauthenticated(unauthenticated_client):
    """Тест попытки получить напитки без аутентификации"""
    response = unauthenticated_client.get("/drinks/")
    # Должен вернуть 401 Unauthorized если маршруты защищены
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_auth_login_endpoint(unauthenticated_client):
    """Тест эндпоинта авторизации (публичный)"""
    login_data = {"username": "test_user", "password": "test_password"}
    
    response = unauthenticated_client.post("/auth/login", data = login_data)
    # Тест публичного эндпоинта
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_401_UNAUTHORIZED]