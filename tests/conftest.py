# tests/conftest.py
# tests/conftest.py
import pytest
import asyncio
# from sqlalchemy import text
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.auth.utils import create_access_token
from app.auth.dependencies import get_current_user, get_current_active_user
from app.core.config.database.db_async import get_db
from app.auth.schemas import UserRead
from app.core.models.base_model import Base
from unittest.mock import AsyncMock
# from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app import main
from app.auth.repository import UserRepository
# from tests import config

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
def super_user():
    return {"username": 'admin',
            "email": 'admin@example.com',
            "password": 'admin',
            "is_active": True,
            "is_superuser": True}


# ---- DATABASE MOCK ----
@pytest.fixture(scope="session")
def mock_db_url():
    """URL для тестовой базы данных SQLite"""
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def mock_engine(mock_db_url):
    """Создает асинхронный движок для тестовой базы данных"""
    engine = create_async_engine(
        mock_db_url, echo=False, pool_pre_ping=True, )
    # Создает все таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope=scope)
async def test_db_session(mock_engine):
    """Создает сессию для тестовой базы данных"""
    AsyncSessionLocal = sessionmaker(bind=mock_engine,
                                     class_=AsyncSession,
                                     expire_on_commit=False, autoflush=False)

    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope=scope)
async def create_superuser(test_db_session, super_user):
    user_repo = UserRepository()
    try:
        new_user = await user_repo.create(super_user, test_db_session)
    except Exception as e:
        print(f"Failed to create superuser: {e}")
        new_user = None
    finally:
        return new_user

# --------FAST API ----------


@pytest.fixture(scope=scope)
def override_app_dependency():
    """Фикстура для переопределения зависимостей приложения"""
    original_overrides = main.app.dependency_overrides.copy()
    yield main.app.dependency_overrides
    main.app.dependency_overrides.update(original_overrides)


@pytest.fixture(scope=scope)
async def authenticated_client_with_db(test_db_session, super_user, override_app_dependency, base_url):
    """ Аутентифицированный клиент с тестовой базой данных """
    # Переопределяем зависимость get_db
    async def get_test_db():
        yield test_db_session

    override_app_dependency[main.get_db] = get_test_db
    token_data = {"sub": super_user.get('username')}
    # Создаем токен для тестового пользователя
    token = create_access_token(data=token_data)

    # Создаем клиент с токеном в заголовках
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url=base_url,
        # headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
    ) as ac:
        ac.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )
        yield ac


@pytest.fixture(scope=scope)
async def authenticated_client_with_db1(test_db_session, super_user, override_app_dependency, base_url):
    """ Аутентифицированный клиент с тестовой базой данных и авторизацией по логин/пароль"""
    # Переопределяем зависимость get_db
    async def get_test_db():
        yield test_db_session

    override_app_dependency[main.get_db] = get_test_db

    # Создаем клиент без токена
    async with AsyncClient(
        transport=ASGITransport(app=main.app), base_url=base_url,
    ) as ac:

        # Регистрируемся от имени admin через форму логина
        # Отправляем данные формы для OAuth2
        login_data = {key: val for key, val in super_user.items() if key in ('username', 'password')}

        # Выполняем логин
        response = await ac.post("/auth/login", data=login_data)

        if response.status_code == 200:
            # Получаем токен из ответа
            token_data = response.json()
            access_token = token_data.get("access_token")
            if access_token:
                # Устанавливаем заголовок авторизации для последующих запросов
                ac.headers.update({"Authorization": f"Bearer {access_token}"})
        yield ac

# -------------------------END-------------------------------


@pytest.fixture(scope=scope)
def test_user():
    """Тестовый пользователь удалить"""
    return UserRead(id=1,
                    username="admin",
                    email="admin@admin.com",
                    is_active=True,
                    is_superuser=True,
                    created_at="2023-01-01T00:00:00",
                    password='admin')


@pytest.fixture(scope=scope)
def test_admin():
    """Тестовый администратор удалить"""
    return UserRead(id=1,
                    username="admin",
                    email="admin@admin.com",
                    is_active=True,
                    is_superuser=True,
                    created_at="2023-01-01T00:00:00",
                    password='admin')


@pytest.fixture(scope=scope)
def mock_db_session():
    """Mock асинхронной сессии БД"""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.add = AsyncMock()
    mock_session.refresh = AsyncMock()
    return mock_session


@pytest.fixture(scope=scope)
async def mock_get_db(mock_db_session):
    """Mock зависимости get_db"""
    async def _mock_get_db():
        yield mock_db_session

    return _mock_get_db


@pytest.fixture(scope=scope)
async def mock_get_current_user(test_user):
    """Mock зависимости get_current_user"""

    async def _mock_get_current_user():
        return test_user

    return _mock_get_current_user


@pytest.fixture(scope=scope)
async def mock_get_current_active_user(test_admin):
    """Mock зависимости get_current_active_user"""

    async def _mock_get_current_active_user():
        return test_admin

    return _mock_get_current_active_user


@pytest.fixture(scope=scope)
async def async_client(base_url):
    """Базовый асинхронный клиент без аутентификации"""
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url=base_url) as client:
        yield client


@pytest.fixture(scope=scope)
async def async_authenticated_client(
        async_client, mock_get_db, mock_get_current_user, mock_get_current_active_user):
    """Асинхронный клиент с подменёнными зависимостями"""
    # Сохраняем оригинальные зависимости
    original_overrides = app.dependency_overrides.copy()

    # Подменяем все зависимости
    app.dependency_overrides.update(
        {get_db: mock_get_db, get_current_user: mock_get_current_user,
         get_current_active_user: mock_get_current_active_user}
    )

    yield async_client

    # Восстанавливаем оригинальные зависимости
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture(scope=scope)
async def async_client_with_token(test_user, base_url):
    """Асинхронный клиент с реальным токеном в headers"""
    from app.auth.utils import create_access_token

    # Создаём реальный JWT токен
    token = create_access_token({"sub": test_user.username})  # , "user_id": test_user.id})

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url=base_url
    ) as async_client:
        async_client.headers.update(
            {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        )
        # Устанавливаем токен в заголовки
        # async_client.headers.update(
        #    {"Authorization": f"Bearer {token}"}
        # )

        yield async_client

    # Очищаем заголовки после теста
    async_client.headers.pop("Authorization", None)

# ------------------








@pytest.fixture(scope="session")
async def setup_test_database(mock_engine):
    """Создает все таблицы в тестовой базе данных"""
    async with mock_engine.begin() as conn:
        # Создаем все таблицы
        await conn.run_sync(Base.metadata.create_all)
        # Можно также выполнить дополнительные SQL команды если нужно
        # await conn.execute(text("PRAGMA foreign_keys=ON"))  # для SQLite
    yield mock_engine
