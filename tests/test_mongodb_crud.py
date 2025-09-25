# tests/test_mongodb.py
# тесты запускать по одному иначе падают - особенность mongodb

import pytest
from motor.motor_asyncio import AsyncIOMotorClient
# from app.mongodb.config import mongodb
from fastapi import status
from tests.config import settings_db
from datetime import datetime, timedelta, timezone
from app.core.utils.common_utils import jprint
from app.mongodb.utils import ContentTypeDetector

pytestmark = pytest.mark.asyncio


async def test_api_mongo_crud_operations(authenticated_client_with_db, test_db_session, sample_image_paths):
    """Тестирует CRUD операции через API - ДОЛЖЕН ПАДАТЬ при проблемах с MongoDB"""
    client = authenticated_client_with_db
    # 1. Тестируем загрузку изображения
    for n, image in enumerate(sample_image_paths):
        with open(image, 'rb') as f:
            image_content = f.read()
        file_size = len(image_content)
        file_name = image.name
        data = {"description": "Test image for integration test"}
        files = {"file": (file_name, image_content)}
        response = await client.post("/mongodb/images/", files = files, data = data)
        # Проверяем успешность запроса
        assert response.status_code == status.HTTP_200_OK, f"Upload failed: {response.text}"
        assert "id" in response.json(), "Response should contain 'id'"
        assert response.json()["message"] == "Image uploaded successfully", "Wrong success message"

    file_id = response.json()["id"]

    # 2. Тестируем получение списка изображений
    response = await client.get("/mongodb/images/")
    now = datetime.utcnow()
    filter_date = now - timedelta(days = 2)
    iso_date = filter_date.isoformat()
    params = {"after_date": iso_date, "page": 1, "per_page": 10}
    response = await client.get("/mongodb/images/", params=params)
    assert response.status_code == status.HTTP_200_OK, response.text
    assert isinstance(response.json(), dict), "response type is not dict"
    jprint(response.json())
    # for key, val in response.json().items():
    #     jprint(f'==={key}: {val}')
    
    # assert len(response.json()['images']) == n, f"Should have exactly {n} images"

    # 3. Тестируем скачивание изображения
    response = await client.get(f"/mongodb/images/{file_id}")
    assert response.status_code == status.HTTP_200_OK, "Download failed"
    assert response.content == image_content, "Downloaded content doesn't match original?"

    # 4. Тестируем удаление изображения
    response = await client.delete(f"/mongodb/images/{file_id}")
    assert response.status_code == status.HTTP_200_OK, "Delete failed"
    assert response.json()["message"] == "Image deleted successfully", "Wrong delete message"

    # 5. Проверяем что изображение действительно удалено
    response = await client.get(f"/mongodb/images/{file_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, "Image should be deleted"


@pytest.mark.skip
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
