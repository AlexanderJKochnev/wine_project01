# tests/conftest.py
import pytest
import asyncio
import docker
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.auth.utils import create_access_token, get_password_hash
from app.core.models.base_model import Base
from app.auth.models import User
from app.main import app, get_db
# from app.auth.repository import UserRepository
import logging

logger = logging.getLogger(__name__)

scope = 'session'


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
    return "http://testserver"


@pytest.fixture(scope=scope)
def test_user_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "testpassword123"
    }


@pytest.fixture(scope=scope)
def super_user_data():
    return {"username": 'admin',
            "email": 'admin@example.com',
            "password": 'admin',
            "is_active": True,
            "is_superuser": True}


# ---- DATABASE MOCK ----

@pytest.fixture(scope=scope)
def mock_db_url():
    """URL для тестовой базы данных SQLite"""
    # return "sqlite+aiosqlite:///:memory:"
    """URL для тесвтовой базы данных POSTGRESQL"""
    return 'postgresql+asyncpg://test_user:test@localhost:5435/test_db'


@pytest.fixture(scope=scope)
def mock_engine(mock_db_url):
    """Создает движок для подключения к тестовой PostgreSQL в Docker"""
    # URL для подключения к вашей запущенной PostgreSQL
    DATABASE_URL = mock_db_url

    engine = create_async_engine(
        DATABASE_URL, echo=False,  # Установите True для отладки SQL запросов
        pool_pre_ping=True, pool_recycle=300
    )

    # Создаем таблицы
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)

    return engine

    # Очищаем таблицы после тестов
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)

    # await engine.dispose()


@pytest.fixture(scope=scope)
async def test_db_session(mock_engine):
    """Создает сессию для тестовой базы данных"""
    """Создает сессию для каждого теста"""
    async_session_factory = sessionmaker(
        bind=mock_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )

    async with async_session_factory() as session:
        yield session
        # Откатываем транзакцию после каждого теста
        await session.rollback()
        await session.close()


@pytest.fixture(scope=scope)
async def create_test_user(test_db_session, test_user_data):
    """Создает тестового пользователя в базе данных"""
    # Создаем пользователя напрямую в БД
    hashed_password = get_password_hash(test_user_data["password"])
    db_user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        hashed_password=hashed_password
    )
    test_db_session.add(db_user)
    await test_db_session.commit()
    await test_db_session.refresh(db_user)
    return db_user


@pytest.fixture(scope=scope)
async def create_super_user(test_db_session, super_user_data):
    """Создает суперпользователя в базе данных"""
    hashed_password = get_password_hash(super_user_data["password"])
    db_user = User(
        username=super_user_data["username"],
        email=super_user_data["email"],
        is_superuser=super_user_data["is_superuser"],
        hashed_password=hashed_password
    )
    test_db_session.add(db_user)
    await test_db_session.commit()
    await test_db_session.refresh(db_user)
    return db_user
# --------FAST API ----------------------------


@pytest.fixture(scope=scope)
async def override_app_dependencies():
    """Фикстура для переопределения зависимостей приложения"""
    original_overrides = app.dependency_overrides.copy()
    yield app.dependency_overrides
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture(scope=scope)
async def get_test_db(test_db_session, create_test_user, create_super_user):
    """Dependency override для получения тестовой сессии БД"""
    yield test_db_session


@pytest.fixture(scope=scope)
async def client(test_db_session, override_app_dependencies, get_test_db, base_url):
    """Базовый клиент без авторизации"""
    # Переопределяем зависимость get_db
    async def get_test_db():
        yield test_db_session
    app.dependency_overrides[get_db] = get_test_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=base_url
    ) as ac:
        yield ac


@pytest.fixture(scope=scope)
async def authenticated_client_with_db(test_db_session, super_user_data,
                                       override_app_dependencies, base_url, get_test_db):
    """ Аутентифицированный клиент с тестовой базой данных """
    """ переобъявление get_test_db в теле - заставляет работать чудо какое-то"""
    async def get_test_db():
        yield test_db_session

    # override_app_dependencies[app.dependency_overrides] = get_test_db
    app.dependency_overrides[get_db] = get_test_db
    # Создаем JWT токен для тестового пользователя
    token_data = {"sub": super_user_data["username"]}
    access_token = create_access_token(data=token_data)

    # Создаем клиент с токеном в заголовках
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url=base_url,
        headers={"Authorization": f"Bearer {access_token}"}
    ) as ac:
        ac._test_user = super_user_data
        ac._test_user_db = create_super_user
        ac._access_token = access_token
        yield ac
