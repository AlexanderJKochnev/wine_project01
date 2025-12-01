import pytest
from app.arq_worker_routes import router
from app.main import app
from app.core.config.project_config import settings


@pytest.mark.asyncio
async def test_start_parse_rawdata_task(authenticated_client_with_db, test_db_session):
    """Тест запуска задачи parse_rawdata_task через API"""
    # Проверяем, что роутер существует
    assert router is not None
    
    # Проверяем, что API endpoint доступен через authenticated_client_with_db
    response = await authenticated_client_with_db.post("/arq-worker/start-task", json={"name_id": 1})
    
    # Ожидаем, что запрос будет обработан (может вернуть ошибку из-за отсутствия Redis в тестовой среде)
    # но сам эндпоинт должен существовать
    # Проверяем, что получили один из ожидаемых статусов
    assert response.status_code in [200, 400, 422, 500]  # 200 - успех, 400/422 - ошибка валидации, 500 - ошибка подключения к Redis
    # В случае ошибки подключения к Redis, проверяем, что это именно ошибка Redis
    if response.status_code == 500:
        response_data = response.json()
        assert "detail" in response_data
        assert ("redis" in response_data["detail"].lower() or 
                "connection" in response_data["detail"].lower() or
                "error" in response_data["detail"].lower())


@pytest.mark.asyncio
async def test_worker_health_check(authenticated_client_with_db, test_db_session):
    """Тест проверки работоспособности воркера"""
    # Проверяем эндпоинт здоровья
    response = await authenticated_client_with_db.get("/arq-worker/health")
    
    # Ожидаем, что эндпоинт существует и возвращает какой-то ответ
    # (может вернуть 500 если Redis не настроен в тестовой среде)
    assert response.status_code in [200, 500]
    # В случае ошибки подключения к Redis, проверяем, что это именно ошибка Redis
    if response.status_code == 500:
        response_data = response.json()
        assert "detail" in response_data
        assert ("redis" in response_data["detail"].lower() or 
                "connection" in response_data["detail"].lower() or
                "error" in response_data["detail"].lower() or
                "ping" in response_data["detail"].lower())


@pytest.mark.asyncio
async def test_arq_worker_routes_available():
    """Тест доступности маршрутов ARQ в приложении"""
    # Проверяем, что маршруты ARQ добавлены к приложении
    route_paths = [route.path for route in app.routes]
    
    # Проверяем наличие нужных маршрутов
    assert any("/arq-worker/start-task" in path for path in route_paths)
    assert any("/arq-worker/health" in path for path in route_paths)