# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.auth.utils import create_access_token, get_password_hash
from app.core.models.base_model import Base
from app.auth.models import User
from app.main import app, get_db
from fastapi.routing import APIRoute
from typing import List, Dict, Any
from tests.utility.data_generators import FakeData
from tests.utility.find_models import discover_models, discover_schemas2


scope = 'session'
scope2 = 'session'
example_count = 50      # количество тестовых записей - рекомедуется >20 для paging test


def get_routers(method: str = 'GET') -> List[APIRoute]:
    """  список роутеров, содержащих указанный метод """
    # prefix содердится в a.path
    exc_route = ('/', '/auth/token', '/wait')
    return [a for a in app.routes
            if all((isinstance(a, APIRoute), a.path not in exc_route)) and all((hasattr(a, 'methods'),
                                                                                method in a.methods))]


@pytest.fixture(scope=scope)
def event_loop(request):
    """
    Создаём отдельный event loop для всей сессии тестов.
    Это предотвращает ошибку "Event loop is closed".
    """
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    try:
        yield loop
    finally:
        if not loop.is_closed():
            loop.close()
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_models():
    """Автоматически обнаруживает все модели для тестирования"""
    return discover_models()


@pytest.fixture(scope=scope)
def get_schemas(discovery_schemas):
    """only read schemas and paginated / delete responses
        получает словарь {schema_name: obj} и преобрузет в словарь
        {model_name:{'create': obj,
                     'update': obj,
                     'read': obj
                     }
        }
    """
    tmp = discover_schemas2(app)
    schemas = {}
    for name, obj in tmp.items():
        if name.endswith('Create'):
            model_name = name[:-6]
            if model_name not in schemas:
                schemas[model_name] = {}
            schemas[model_name]['create'] = obj
        elif name.endswith('Update'):
            model_name = name[:-6]
            if model_name not in schemas:
                schemas[model_name] = {}
            schemas[model_name]['update'] = obj
        elif name.endswith('Read'):
            model_name = name[:-4]
            if model_name not in schemas:
                schemas[model_name] = {}
            schemas[model_name]['read'] = obj
    return schemas


@pytest.fixture(scope=scope)
def discovery_schemas():
    return discover_schemas2(app)


@pytest.fixture(scope="session")
async def test_schemas(authenticated_client_with_db, test_db_session):
    client = authenticated_client_with_db
    schemas = {}
    response = await client.get("/openapi.json")
    assert response.status_code == 200
    openapi = response.json()
    # Все компоненты (включая схемы)
    tmp = openapi["components"]["schemas"]
    for name, obj in tmp.items():
        if name.endswith('Create'):
            model_name = name[:-6]
            if model_name not in schemas:
                schemas[model_name] = {}
            schemas[model_name]['create'] = obj
        elif name.endswith('Update'):
            model_name = name[:-6]
            if model_name not in schemas:
                schemas[model_name] = {}
            schemas[model_name]['update'] = obj
        elif name.endswith('Read'):
            model_name = name[:-4]
            if model_name not in schemas:
                schemas[model_name] = {}
            schemas[model_name]['read'] = obj
    return schemas


@pytest.fixture(scope=scope)
def base_url():
    return "http://testserver"


@pytest.fixture(scope=scope)
def get_fields_type() -> Dict[str, Any]:
    """
        Подготавливает спиcок имен полей и генераторов их значений для всех POST/PATCH
        маршрутов, отсортированных по очередности заполнения
        {
        route: /example,
        method: 'POST' | 'PATCH'
        model_name: 'DrinkCreate' (schema name)
        test_data {required_only: {field: generator ...},
                   all_fields: {field: generator ...}
        }
    """
    x = FakeData(app, 1)
    return x()


@pytest.fixture(scope=scope)
async def fakedata_generator(authenticated_client_with_db, test_db_session, get_fields_type):
    """
    проходит по списку роутеров и заполняет таблицы данными
    :return:
    :rtype:
    """
    client = authenticated_client_with_db
    counts = 5
    for key, val in get_fields_type.items():
        for n in range(counts):
            route = key
            if n % 2 == 0:
                data = {k2: v2() for k2, v2 in val['required_only'].items()}
            else:
                try:
                    data = {k2: v2() for n, (k2, v2) in enumerate(val['all_fields'].items())}
                except Exception as e:
                    print(f'ошибка {e}  {val['all_fields']}')
            response = await client.post(f'{route}', json=data)
            assert response.status_code == 200, f'{route=} {data=} {key=}'


@pytest.fixture(scope=scope)
def routers_get_one() -> List[str]:
    """ список роутеров GET get_by_id"""
    return [x.path for x in get_routers('GET') if x.name == 'get_one']


@pytest.fixture(scope=scope)
def routers_get_all() -> List[APIRoute]:
    """ список роутеров GET get_all"""
    return [x.path for x in get_routers('GET') if x.name == 'get']


@pytest.fixture(scope=scope)
def routers_post() -> List[str]:
    return [x for x in get_routers('POST')]


@pytest.fixture(scope=scope)
def routers_patch() -> List[str]:
    return [x.path for x in get_routers('PATCH')]


@pytest.fixture(scope=scope)
def routers_delete() -> List[str]:
    return [x.path for x in get_routers('DELETE')]


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
    # return "postgresql+asyncpg://test_user:test@localhost:2345/test_db"
    return "postgresql+psycopg_async://test_user:test@localhost:2345/test_db"
    # return "sqlite+aiosqlite:///:memory:?cache=shared"


@pytest.fixture(scope=scope)
async def mock_engine(mock_db_url):
    """Создает асинхронный движок для тестовой базы данных"""
    engine = create_async_engine(
        mock_db_url,
        echo=False,
        pool_pre_ping=True
    )
    # Создает все таблицы в базе данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest.fixture(scope=scope2)
async def test_db_session(mock_engine):
    """Создает сессию для тестовой базы данных"""
    AsyncSessionLocal = sessionmaker(
        bind=mock_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
    )
    # async with mock_engine.connect() as session:
    async with AsyncSessionLocal() as session:
        yield session
        await session.close()


@pytest.fixture(scope=scope2)
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


@pytest.fixture(scope=scope2)
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


@pytest.fixture(scope=scope2)
async def get_test_db(test_db_session, create_test_user, create_super_user):
    """Dependency override для получения тестовой сессии БД"""
    yield test_db_session


@pytest.fixture(scope=scope2)
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


@pytest.fixture(scope=scope2)
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

# -----------data generator------------------
