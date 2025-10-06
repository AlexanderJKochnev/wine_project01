# tests/test_mongodb.py
# тесты запускать по одному иначе падают - особенность mongodb

import pytest
# from app.mongodb.config import mongodb
from fastapi import status

from app.mongodb.router import prefix, subprefix

pytestmark = pytest.mark.asyncio


async def test_api_mongo_crud_operations(authenticated_client_with_db,
                                         test_db_session,
                                         sample_image_paths,
                                         todayutc,
                                         futureutc,
                                         pastutc):
    """Тестирует CRUD операции через API - ДОЛЖЕН ПАДАТЬ при проблемах с MongoDB"""
    client = authenticated_client_with_db
    # 1. Тестируем загрузку изображения
    for n, image in enumerate(sample_image_paths):
        with open(image, 'rb') as f:
            image_content = f.read()
        # file_size = len(image_content)
        file_name = image.name
        data = {"description": "Test image for integration test"}
        files = {"file": (file_name, image_content)}
        response = await client.post(f'{prefix}/{subprefix}', files=files, data=data)
        # Проверяем успешность запроса
        assert response.status_code == status.HTTP_200_OK, f"Upload failed: {response.text}"
        assert "id" in response.json(), "Response should contain 'id'"
        assert response.json()["message"] == "Image uploaded successfully", "Wrong success message"
    file_id = response.json()["id"]

    # 2. Тестируем получение списка изображений
    # response = await client.get(f"{prefix}{subprefix}")
    # now = datetime.utcnow()
    # filter_date = now - timedelta(days = 2)
    # iso_date = filter_date.isoformat()
    # params = {"after_date": iso_date, "page": 1, "per_page": 10}
    # дата по умолчанию
    params = [({"page": 1, "per_page": 10}, 200, n),
              ({"page": 1, "per_page": 10, "after_date": pastutc}, 200, n),
              ({"page": 1, "per_page": 10, "after_date": todayutc}, 200, 0),
              ({"page": 1, "per_page": 10, "after_date": futureutc}, 400, 0),
              ]
    for param, sts, nmb in params:
        response = await client.get(f"{prefix}/{subprefix}", params=param)
        assert response.status_code == sts, f'{param=}, response.text'
        assert isinstance(response.json(), dict), "response type is not dict"
        param = {'after_date': param.get('after_date')} if param.get('after_date') else None
        response = await client.get(f"{prefix}/{subprefix}list", params=param)
        assert response.status_code == sts, f'{param=}'
        if response.status_code != 400:
            assert isinstance(response.json(), dict), f"response type is {response.json()}. {response.status_code}"

    # 3. Тестируем скачивание изображения (подвешивает тест разобраться)
    """
    response = await client.get(f"{prefix}{subprefix}/{file_id}")
    assert response.status_code == status.HTTP_200_OK, "Download failed"
    assert response.content == image_content, "Downloaded content doesn't match original?"
    assert False
    """
    # 4. Тестируем удаление изображения
    response = await client.delete(f"{prefix}/{subprefix}/{file_id}")
    assert response.status_code == status.HTTP_200_OK, "Delete failed"
    assert response.json()["message"] == "Image deleted successfully", "Wrong delete message"

    # 5. Проверяем что изображение действительно удалено
    response = await client.get(f"{prefix}/{subprefix}/{file_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND, "Image should be deleted"


# @pytest.mark.skip
async def test_api_authentication_required(test_client_with_mongo):
    """Тестирует что аутентификация обязательна для MongoDB endpoints"""
    client = test_client_with_mongo

    # Убираем аутентификацию
    if "Authorization" in client.headers:
        del client.headers["Authorization"]

    # Пытаемся получить доступ без аутентификации
    response = await client.get(f"{prefix}/{subprefix}")

    # Должен вернуть 401
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, "Should require authentication"
# --------------------------------------
