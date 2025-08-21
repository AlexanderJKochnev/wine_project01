# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.utils import create_access_token, get_password_hash


@pytest.fixture(scope = "function")
def event_loop():
    """Создаём event loop для каждого теста"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope = "function")
async def test_db():
    """Создает тестовую базу данных"""
    # Используем in-memory SQLite для тестов
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo = False)
    
    # Создаем все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session_factory = sessionmaker(
            bind = engine, class_ = AsyncSession, expire_on_commit = False, autoflush = False
            )
    
    async with async_session_factory() as session:
        yield session
    
    await engine.dispose()


@pytest.fixture(scope = "function")
async def client(test_db):
    """Клиент для тестирования"""
    
    # Переопределяем зависимость get_db
    def override_get_db():
        async def _get_test_db():
            yield test_db
        
        return _get_test_db
    
    app.dependency_overrides[get_db] = override_get_db()
    
    async with AsyncClient(
            transport = ASGITransport(app = app), base_url = "http://test"
            ) as ac:
        yield ac
    
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture(scope = "function")
async def test_user_data():
    """Тестовые данные пользователя"""
    return {"username": "testuser", "email": "test@example.com", "full_name": "Test User",
            "password": "testpassword123"}


@pytest.fixture(scope = "function")
async def create_test_user(test_db, test_user_data):
    """Создает тестового пользователя в БД"""
    hashed_password = get_password_hash(test_user_data["password"])
    from app.models import User
    db_user = User(
            username = test_user_data["username"], email = test_user_data["email"],
            full_name = test_user_data["full_name"], hashed_password = hashed_password, disabled = False
            )
    
    test_db.add(db_user)
    await test_db.commit()
    await test_db.refresh(db_user)
    return db_user


@pytest.fixture(scope = "function")
async def authenticated_client(client, test_user_data, create_test_user):
    """Аутентифицированный клиент"""
    # Создаем JWT токен
    token_data = {"sub": test_user_data["username"]}
    access_token = create_access_token(data = token_data)
    
    # Устанавливаем заголовок авторизации
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    client._test_user = test_user_data
    client._access_token = access_token
    
    return client