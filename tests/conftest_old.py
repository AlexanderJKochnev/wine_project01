# tests/conftest.py

import asyncio
import logging
import pytest
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
from app import main
from tests import config
from app.auth.schemas import UserRead
from app.auth.utils import create_access_token

# from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.models.base_model import Base

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
async def authenticated_client(super_user, base_url):
    """Аутентифицированный клиент для тестирования (через токен для middleware)"""
    # Создаем токен для тестового пользователя
    from app.core.config.database.db_async import get_db
    app = main.app
    token = create_access_token(data={"sub": super_user.username})
    print("\n" + "=" * 50)
    print("ДО подмены зависимостей:")
    for dep, override in app.dependency_overrides.items():
        print(f"  {dep.__name__}: {override}")
    original_overrides = main.app.dependency_overrides.copy()
    app.dependency_overrides.update({get_db: mock_db_session})
    print("ПОСЛЕ подмены зависимостей:")
    for dep, override in app.dependency_overrides.items():
        print(f"  {dep.__name__}: {override}")
    print("=" * 50 + "\n")
    # main.app.dependency_overrides[get_db] = mock_db_session
    # Создаем клиент с токеном в заголовках
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url='http://testserver',
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


# ----database mocking fixtures -----------

@pytest.fixture(scope=scope)
def mock_db_url():
    """Создает временную базу данных SQLite для тестов"""
    # Создаем временную базу данных в памяти
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope=scope)
async def mock_db_engine(mock_db_url):
    """Создает асинхронный движок для тестовой базы данных"""
    engine = create_async_engine(
        mock_db_url, echo=False, pool_pre_ping=True, )
    yield engine
    await engine.dispose()


@pytest.fixture(scope=scope)
async def mock_db_session_factory(mock_db_engine):
    """Создает фабрику сессий для тестовой базы данных"""
    async with mock_db_engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        bind=mock_db_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    yield AsyncSessionLocal


@pytest.fixture
async def mock_db_session(mock_db_session_factory):
    """Создает сессию для тестовой базы данных"""
    async with mock_db_session_factory() as session:
        yield session


@pytest.fixture(scope=scope)
async def authenticated_client_with_mock_db(super_user, mock_db_session_factory):
    """Аутентифицированный клиент с mock базой данных"""
    from fastapi import FastAPI
    # from fastapi.testclient import TestClient

    # Создаем новое приложение для тестов
    app = FastAPI()

    # Здесь нужно добавить все роутеры, которые используются в тестах
    from app.support.category.router import router as category_router
    from app.support.drink.router import router as drink_router
    from app.support.country.router import router as country_router
    from app.support.customer.router import router as customer_router
    from app.support.warehouse.router import router as warehouse_router
    from app.support.food.router import router as food_router
    from app.support.item.router import router as item_router
    from app.support.region.router import router as region_router
    from app.support.color.router import router as color_router
    from app.support.sweetness.router import router as sweetness_router
    from app.core.routers.image_router import router as image_router
    # from app.core.security import get_current_active_user

    app.include_router(drink_router)
    app.include_router(category_router)
    app.include_router(country_router)
    app.include_router(customer_router)
    app.include_router(warehouse_router)
    app.include_router(food_router)
    app.include_router(item_router)
    app.include_router(region_router)
    app.include_router(color_router)
    app.include_router(sweetness_router)
    app.include_router(image_router)

    # Создаем токен для тестового пользователя
    token = create_access_token(data={"sub": super_user.username})

    # Создаем клиент с токеном в заголовках
    client = TestClient(app)
    client.headers.update({"Authorization": f"Bearer {token}"})

    yield client


async def fastapi_test_app_with_mock_db():
    """Создает FastAPI приложение с mock базой данных"""
    # Переопределяем зависимости для использования mock базы
    from app.core.config.database.db_async import AsyncSessionLocal
    from app.core.config.database.db_async import get_db

    # Сохраняем оригинальную фабрику сессий
    original_session_factory = AsyncSessionLocal

    # Здесь можно переопределить get_db dependency если нужно
    yield main.app

    # Восстанавливаем оригинальную фабрику (если нужно)


@pytest.fixture(scope=scope)
async def authenticated_client_mock_db(super_user):
    """Аутентифицированный клиент для тестирования с mock базой данных"""
    # Создаем токен для тестового пользователя
    token = create_access_token(data={"sub": super_user.username})

    # Создаем клиент с токеном в заголовках
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url="http://testserver",
        headers={"Authorization": f"Bearer {token}"}
    ) as ac:
        yield ac
