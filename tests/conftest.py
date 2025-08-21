# tests/conftest.py
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from app.auth.utils import create_access_token
from app.core.models.base_model import Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app import main
from app.auth.repository import UserRepository

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
@pytest.fixture(scope=scope)
def mock_db_url():
    """URL для тестовой базы данных SQLite"""
    return "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope=scope)
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
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"}
    ) as ac:
        # ac.headers.update(
        #     {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        # )
        yield ac


@pytest.fixture(scope=scope)
async def authenticated_client_with_db1(test_db_session, create_superuser, super_user, override_app_dependency,
                                        base_url):
    """ Аутентифицированный клиент с тестовой базой данных и авторизацией по логин/пароль"""
    # Переопределяем зависимость get_db
    token_data = {"sub": super_user.get('username')}
    # Создаем токен для сравнения
    token = create_access_token(data=token_data)

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
            print(f'{token_data=}')
            access_token = token_data.get("access_token")
            print(f'----------------{access_token == token=}')
            if access_token:
                # Устанавливаем заголовок авторизации для последующих запросов
                ac.headers.update({"Authorization": f"Bearer {access_token}"})
        yield ac


@pytest.fixture(scope=scope)
async def unauthenticated_client_with_db(test_db_session, override_app_dependency, base_url):
    """ Аутентифицированный клиент с тестовой базой данных и авторизацией по логин/пароль"""
    # не работает !!!
    # Переопределяем зависимость get_db
    async def get_test_db():
        yield test_db_session

    override_app_dependency[main.get_db] = get_test_db

    # Создаем клиент без токена
    async with AsyncClient(transport=ASGITransport(app=main.app), base_url=base_url, ) as ac:
        # Регистрируемся от имени admin через форму логина
        yield ac

# -------------------------END-------------------------------
@pytest.fixture(scope=scope)
async def admin_client():
    """Клиент для тестирования админки"""
    async with AsyncClient(
        transport=ASGITransport(app=main.app),
        base_url="http://test"
    ) as client:
        yield client