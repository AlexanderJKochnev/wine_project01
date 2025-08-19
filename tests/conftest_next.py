# tests/conftest.py

import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
# from app.auth.models import User
from app.auth.schemas import UserRead
from app.auth.repository import UserRepository
from app.auth.utils import create_access_token
from app.auth.dependencies import get_current_active_user, get_current_user
from app.core.config.database.db_async import AsyncSessionLocal
from tests import config
# from sqlalchemy import select


@pytest.fixture(scope='session')
def base_url():
    return config.base_url_doc


@pytest.fixture(scope="session")
def event_loop():
    """Создание event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# @pytest.fixture(scope="session")
@pytest.fixture
async def async_client(base_url):
    """Асинхронный клиент без аутентификации"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url=base_url) as ac:
        yield ac


@pytest.fixture
def superuser():
    """Создание тестового суперпользователя"""
    user_data = UserRead(id=1,
                         username="test_admin",
                         email="admin@test.com",
                         is_active=True,
                         is_superuser=True,
                         created_at="2023-01-01T00:00:00"
                         )
    return user_data


@pytest.fixture(scope="session")
def logged_in_user_real(super_user):
    """ подстановка пользователя для запуска клиента без моков """
    test_user = super_user
    # app.include_router(testrouter)
    # injection test user to app
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_current_active_user] = lambda: test_user
    # pp.plugin_injection(app)
    return app, original_overrides


@pytest.fixture
async def authenticated_client(base_url, superuser):
    """Асинхронный клиент с подменой зависимости для аутентификации"""
    # Подменяем зависимости
    async with AsyncClient(transport=ASGITransport(app=app), base_url=base_url) as client:
        # original_overrides = app.dependency_overrides.copy()
        # app.dependency_overrides[get_current_active_user] = lambda: superuser
        # app.dependency_overrides[get_current_user] = lambda: superuser

        yield client  # ✅ yield уже существующий клиент

    # Восстанавливаем зависимости
    # app.dependency_overrides.clear()
    # app.dependency_overrides.update(original_overrides)  # Контекстный менеджер async_client закроется в своей fixture


@pytest.fixture
async def create_test_user_in_db():
    """Создание тестового пользователя в БД"""
    async with AsyncSessionLocal() as session:
        user_repo = UserRepository()

        # Проверяем, существует ли уже тестовый пользователь
        existing_user = await user_repo.get_by_field("username", "test_user", session)
        if existing_user:
            return existing_user

        # Создаем тестового пользователя
        user_data = {"username": "test_user",
                     "email": "test@example.com",
                     "password": "test_password",
                     "is_active": True,
                     "is_superuser": True}

        user = await user_repo.create(user_data, session)
        return user


@pytest.fixture
async def get_test_token(create_test_user_in_db):
    """Получение токена для тестового пользователя"""
    user = create_test_user_in_db
    token = create_access_token(data={"sub": user.username})
    return token


@pytest.fixture
async def authenticated_client_real(async_client, get_test_token):
    """Асинхронный клиент с реальной аутентификацией через токен"""
    # Сохраняем оригинальные заголовки
    original_headers = async_client.headers.copy()
    # Добавляем токен в заголовки
    async_client.headers.update(
        {"Authorization": f"Bearer {get_test_token}"}
    )

    yield async_client

    # Восстанавливаем оригинальные заголовки
    async_client.headers.clear()
    async_client.headers.update(original_headers)


@pytest.fixture
async def unauthenticated_client(async_client):
    """Асинхронный клиент без аутентификации"""
    # Убедимся, что нет подмененных зависимостей
    original_overrides = app.dependency_overrides.copy()
    app.dependency_overrides.clear()

    yield async_client

    # Восстанавливаем зависимости
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
