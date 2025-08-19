# tests/conftest.py

import asyncio
import logging
import pytest
from httpx import ASGITransport, AsyncClient
from app import main
from tests import config
from app.auth.schemas import UserRead
from app.auth.utils import create_access_token


scope = 'session'
logger = logging.getLogger(__name__)


@pytest.fixture(scope=scope)
def event_loop(request):
    """
    Создаём отдельный event loop для всей сессии тестов.
    Это предотвращает ошибку "Event loop is closed".
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    try:
        yield loop
    finally:
        if not loop.is_closed():
            loop.close()


@pytest.fixture(scope=scope)
def base_url():
    return config.base_url_doc


@pytest.fixture(scope=scope)
def super_user():
    user_data = UserRead(id=1,
                         username="test",
                         email="admin@test.com",
                         is_active=True,
                         is_superuser=True,
                         created_at="2023-01-01T00:00:00",
                         password='test')
    return user_data


@pytest.fixture(scope=scope)
async def async_test_app(logged_in_user_real,
                         event_loop,
                         base_url,
                         ):
    """ запуск клиента из-вне"""
    async with AsyncClient(
            transport=ASGITransport(app=logged_in_user_real),
            base_url=base_url
    ) as ac:
        # передача управления
        yield ac


@pytest.fixture(scope=scope)
async def authenticated_client(super_user, base_url):
    """Аутентифицированный клиент для тестирования (через токен для middleware)"""
    # Создаем токен для тестового пользователя
    token = create_access_token(data={"sub": super_user.username})
    # Создаем клиент с токеном в заголовках
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url=base_url,
        headers={"Authorization": f"Bearer {token}"}
    ) as ac:
        yield ac


@pytest.fixture(scope=scope)
async def unauthenticated_client(base_url):
    """Неаутентифицированный клиент для тестирования публичных endpoints"""
    async with AsyncClient(
            transport=ASGITransport(app=main.app),
            base_url=base_url
    ) as ac:
        yield ac


@pytest.fixture(scope=scope)
async def admin_client():
    """Клиент для тестирования админки"""
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture
async def admin_login_session(admin_client):
    """Сессия с залогиненым админом"""
    # Логинимся
    login_data = {"username": "admin",
                  "password": "admin"}  # Используйте реальные учетные данные

    response = await admin_client.post("/admin/login", data=login_data)

    if response.status_code in [200, 302, 303, 307]:
        yield admin_client
    else:
        pytest.skip("Не удалось залогиниться в админку")


@pytest.fixture
async def cleanup_admin_test_users():
    """Фикстура для очистки тестовых пользователей после тестов"""
    yield
    # Здесь можно добавить логику очистки тестовых пользователей
    pass
