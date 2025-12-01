import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.arq_worker_routes import router


client = TestClient(app)


@pytest.mark.asyncio
async def test_start_parse_rawdata_task():
    """Тест запуска задачи parse_rawdata_task через API"""
    with patch("app.arq_worker_routes.create_pool") as mock_create_pool:
        # Мок для пула ARQ
        mock_pool = AsyncMock()
        mock_job = AsyncMock()
        mock_job.job_id = "test_job_id"
        mock_pool.enqueue_job.return_value = mock_job
        mock_create_pool.return_value = mock_pool
        
        # Вызов API
        response = client.post("/arq-worker/start-task", json={"name_id": 1})
        
        # Проверки
        assert response.status_code == 200
        assert response.json() == {"message": "Task started successfully", "job_id": "test_job_id"}
        
        # Проверяем, что enqueue_job был вызван с правильными параметрами
        mock_pool.enqueue_job.assert_called_once_with("parse_rawdata_task", 1)


@pytest.mark.asyncio
async def test_start_parse_rawdata_task_with_job_id():
    """Тест запуска задачи parse_rawdata_task с указанным job_id"""
    with patch("app.arq_worker_routes.create_pool") as mock_create_pool:
        # Мок для пула ARQ
        mock_pool = AsyncMock()
        mock_job = AsyncMock()
        mock_job.job_id = "specified_job_id"
        mock_pool.enqueue_job.return_value = mock_job
        mock_create_pool.return_value = mock_pool
        
        # Вызов API с job_id
        response = client.post("/arq-worker/start-task", json={"name_id": 1, "job_id": "specified_job_id"})
        
        # Проверки
        assert response.status_code == 200
        assert response.json() == {"message": "Task started successfully", "job_id": "specified_job_id"}
        
        # Проверяем, что enqueue_job был вызван с правильными параметрами
        mock_pool.enqueue_job.assert_called_once_with("parse_rawdata_task", 1, _job_id="specified_job_id")


@pytest.mark.asyncio
async def test_worker_health_check():
    """Тест проверки работоспособности воркера"""
    with patch("app.arq_worker_routes.create_pool") as mock_create_pool:
        # Мок для пула ARQ
        mock_pool = AsyncMock()
        mock_pool.ping.return_value = None  # Успешный ping
        mock_create_pool.return_value = mock_pool
        
        # Вызов API
        response = client.get("/arq-worker/health")
        
        # Проверки
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "message": "ARQ worker is ready to process tasks"}
        
        # Проверяем, что ping был вызван
        mock_pool.ping.assert_called_once()


@pytest.mark.asyncio
async def test_worker_health_check_failure():
    """Тест проверки работоспособности воркера при ошибке"""
    with patch("app.arq_worker_routes.create_pool") as mock_create_pool:
        # Мок для пула ARQ, который выбрасывает исключение
        mock_pool = AsyncMock()
        mock_pool.ping.side_effect = Exception("Connection failed")
        mock_create_pool.return_value = mock_pool
        
        # Вызов API
        response = client.get("/arq-worker/health")
        
        # Проверки
        assert response.status_code == 500
        assert "Worker health check failed" in response.json()["detail"]