# tests/test_mongodb.py
# тесты запускать по одному иначе падают - особенность mongodb

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
# from app.mongodb.config import mongodb
from fastapi import status
from tests.config import settings_db

pytestmark = pytest.mark.asyncio

async def test_api_health_endpoint(test_client_with_mongo):
    """Тестирует health endpoint через API - ДОЛЖЕН ПАДАТЬ при отсутствии MongoDB"""
    client = test_client_with_mongo

    response = await client.get("/health")

    # Проверяем статус код
    assert response.status_code == status.HTTP_200_OK, f"Health endpoint returned {response.status_code}"

    data = response.json()

    # Проверяем структуру ответа
    assert "status" in data, "Missing 'status' in health response"
    assert "mongo_connected" in data, "Missing 'mongo_connected' in health response"
    assert "mongo_operational" in data, "Missing 'mongo_operational' in health response"

    # Проверяем значения - ДОЛЖНЫ БЫТЬ True
    assert data["mongo_connected"] is True, "MongoDB should be connected"
    assert data["mongo_operational"] is True, "MongoDB should be operational"
    assert data["status"] == "healthy", f"Status should be 'healthy', got '{data['status']}'"
