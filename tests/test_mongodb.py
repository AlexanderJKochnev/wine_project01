# tests/test_mongodb.py
# тесты запускать по одному иначе падают - особенность mongodb

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
# from app.mongodb.config import mongodb
from fastapi import status
from tests.config import settings_db

pytestmark = pytest.mark.asyncio


async def test_direct_mongo_connection():
    """Прямое тестирование подключения к MongoDB"""
    try:
        mongo_url = settings_db.mongo_url
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=500)
        # Проверяем подключение
        await client.admin.command('ping')
        client.close()
        assert True, "MongoDB connection unsuccessful"
    except Exception as e:
        print(f"Direct connection failed: {e}")
        assert False, f"{e} {mongo_url=}"


async def test_mongo_health_check(test_mongodb):
    """Тестирует health check MongoDB подключения - ДОЛЖЕН ПАДАТЬ при проблемах"""
    # Проверяем что можем выполнять команды
    try:
        result = await test_mongodb.client.admin.command('ping')
        assert result["ok"] == 1.0, "MongoDB ping command failed"
    except Exception as e:
        pytest.fail(f"MongoDB health check failed: {e}")


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


async def test_api_mongo_crud_operations(authenticated_client_with_db, test_db_session):
    """Тестирует CRUD операции через API - ДОЛЖЕН ПАДАТЬ при проблемах с MongoDB"""
    client = authenticated_client_with_db
    # 1. Тестируем загрузку изображения
    tier = 10
    for i in range(tier):
        test_image_data = b"fake_image_data_123"
        files = {"file": (f"test{i}.jpg", test_image_data, "image/jpeg")}
        data = {"description": "Test image for integration test"}
        response = await client.post("/mongodb/images/", files=files, data=data)
        # Проверяем успешность запроса
        assert response.status_code == status.HTTP_200_OK, f"Upload failed: {response.text}"
        assert "id" in response.json(), "Response should contain 'id'"
        assert response.json()["message"] == "Image uploaded successfully", "Wrong success message"

    file_id = response.json()["id"]

    # 2. Тестируем получение списка изображений
    response = await client.get("/mongodb/images/")
    assert response.status_code == status.HTTP_200_OK, "Get images list failed"
    assert isinstance(response.json(), list), "Response should be a list"
    assert len(response.json()) == tier, f"Should have exactly {tier} images"
    assert response.json()[0]["filename"] == "test0.jpg", "Wrong filename"

    # 3. Тестируем скачивание изображения
    response = await client.get(f"/mongodb/images/{file_id}")
    assert response.status_code == status.HTTP_200_OK, "Download failed"
    assert response.content == test_image_data, "Downloaded content doesn't match original"

    # 4. Тестируем удаление изображения
    response = await client.delete(f"/mongodb/images/{file_id}")
    assert response.status_code == status.HTTP_200_OK, "Delete failed"
    assert response.json()["message"] == "Image deleted successfully", "Wrong delete message"

    # 5. Проверяем что изображение действительно удалено
    response = await client.get(f"/mongodb/images/{file_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, "Image should be deleted"


async def test_api_authentication_required(test_client_with_mongo):
    """Тестирует что аутентификация обязательна для MongoDB endpoints"""
    client = test_client_with_mongo

    # Убираем аутентификацию
    if "Authorization" in client.headers:
        del client.headers["Authorization"]

    # Пытаемся получить доступ без аутентификации
    response = await client.get("/mongodb/images/")

    # Должен вернуть 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Should require authentication"
# --------------------------------------
