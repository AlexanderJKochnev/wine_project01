import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.config.project_config import settings
from unittest.mock import patch, AsyncMock
from app.arq_worker_routes import router


@pytest.mark.asyncio
async def test_start_parse_rawdata_task(authenticated_client_with_db):
    """Тест запуска задачи parse_rawdata_task через API"""
    # Mock the ARQ enqueue functionality to avoid needing Redis in tests
    with patch('arq.connections.ArqConnection') as mock_arq_conn:
        mock_enqueue = AsyncMock()
        mock_enqueue.job_id = "test_job_123"
        mock_arq_conn.enqueue = mock_enqueue
        mock_arq_conn.close = AsyncMock()
        
        # Mock the get_redis_pool function to return our mock
        with patch('app.arq_worker_routes.get_redis_pool', return_value=mock_arq_conn):
            response = await authenticated_client_with_db.post(
                "/arq-worker/start-task", 
                json={"name_id": 1}
            )
            
            # Should return 200 if the endpoint works correctly
            assert response.status_code == 200
            response_data = response.json()
            assert "job_id" in response_data


@pytest.mark.asyncio
async def test_worker_health_check(authenticated_client_with_db):
    """Тест проверки работоспособности воркера"""
    # Mock the Redis connection for health check
    with patch('app.arq_worker_routes.get_redis_pool') as mock_get_redis:
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock(return_value=True)
        mock_get_redis.return_value = mock_redis
        
        response = await authenticated_client_with_db.get("/arq-worker/health")
        
        # Should return 200 if the health check works
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == {"status": "healthy", "redis": True}


@pytest.mark.asyncio
async def test_arq_worker_routes_available():
    """Тест доступности маршрутов ARQ в приложении"""
    # Check if ARQ worker routes are registered
    route_paths = [route.path for route in app.routes]
    
    # Check for the presence of ARQ worker routes
    assert any("/arq-worker/start-task" in path for path in route_paths)
    assert any("/arq-worker/health" in path for path in route_paths)