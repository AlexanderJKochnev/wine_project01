# tests/conftest.py
import asyncio
import json
import logging
from typing import Any, Dict, List

import pytest
from fastapi.routing import APIRoute
from httpx import ASGITransport, AsyncClient
from pydantic import TypeAdapter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.auth.models import User
from app.auth.utils import create_access_token, get_password_hash
from app.core.models.base_model import Base
from app.main import app, get_db
from app.mongodb.config import MongoDB, get_mongodb, get_database
# from app.mongodb.router import get_mongodb
from tests.config import settings_db
from tests.data_factory.fake_generator import generate_test_data
from tests.data_factory.reader_json import JsonConverter
from tests.utility.data_generators import FakeData
from tests.utility.find_models import discover_models, discover_schemas2

scope = 'session'
scope2 = 'session'
example_count = 5      # количество тестовых записей - рекомедуется >20 для paging test


@pytest.fixture(scope="session")
async def test_mongodb():
    """Создает тестовый экземпляр MongoDB"""
    test_mongo = MongoDB()
    test_url = f'{settings_db.mongo_url}/test_db'
    await test_mongo.connect(test_url, "test_db")
    yield test_mongo
    await test_mongo.disconnect()


@pytest.fixture(scope="function")  # , autouse=True)
async def clean_database(test_mongodb):
    """Очищает базу данных перед каждым тестом"""
    if test_mongodb.database:
        collections = await test_mongodb.database.list_collection_names()
        for collection_name in collections:
            if not collection_name.startswith('system.'):
                await test_mongodb.database[collection_name].delete_many({})
    yield


@pytest.fixture(scope="function")
async def test_mongo_connection():
    """Фикстура для проверки прямого подключения к MongoDB"""
    try:
        client = AsyncIOMotorClient(settings_db.mongo_url, serverSelectionTimeoutMS=5000)
        await client.admin.command('ping')
        client.close()
        return True
    except Exception as e:
        pytest.fail(f"MongoDB connection failed: {e}")


@pytest.fixture(scope="function")
async def mongo_health_check(test_mongodb):
    """Проверка здоровья MongoDB подключения из приложения"""
    try:
        # Проверяем что можем выполнять команды
        await test_mongodb.client.admin.command('ping')
        return True
    except Exception as e:
        pytest.fail(f"MongoDB health check failed: {e}")

# ---------------mongo db end ----------


def pytest_configure(config):
    config.option.log_cli_level = "INFO"
    config.option.log_cli_format = "%(levelname)s - %(message)s"


@pytest.fixture(autouse=True)
def disable_httpx_logging():
    """Подавляет INFO-логи от httpx и httpcore"""
    loggers_to_silence = ["httpx", "httpx._client", "httpcore"]
    for name in loggers_to_silence:
        logging.getLogger(name).setLevel(logging.WARNING)


@pytest.fixture(scope=scope)
def import_data() -> List[Dict]:
    data = JsonConverter()()
    return list(data.values())


def get_routers(method: str = 'GET') -> List[APIRoute]:
    """  список роутеров, содержащих указанный метод """
    # prefix содердится в a.path
    exc_route = ('/', '/auth/token', '/wait')
    return [a for a in app.routes
            if all((isinstance(a, APIRoute), a.path not in exc_route)) and all((hasattr(a, 'methods'),
                                                                                method in a.methods))]


@pytest.fixture(scope=scope)
def simple_router_list():
    """генератор тестовых данных 1
    """

    from app.support.category.router import CategoryRouter
    # from app.support.color.router import ColorRouter
    from app.support.country.router import CountryRouter
    from app.support.customer.router import CustomerRouter
    from app.support.food.router import FoodRouter
    from app.support.sweetness.router import SweetnessRouter
    from app.support.varietal.router import VarietalRouter

    # generator = TestDataGenerator()
    # template = remove_id(json_reader())
    # return generator.generate(template, count=7)
    source = (CategoryRouter,
              # ColorRouter,
              CountryRouter,
              CustomerRouter,
              FoodRouter,
              SweetnessRouter,
              VarietalRouter)
    return source


@pytest.fixture(scope=scope)
def complex_router_list():
    """ генератор тестовых данных 2"""
    from app.support.subcategory.router import SubcategoryRouter
    from app.support.region.router import RegionRouter
    from app.support.subregion.router import SubregionRouter
    from app.support.warehouse.router import WarehouseRouter
    from app.support.drink.router import DrinkRouter
    from app.support.item.router import ItemRouter
    return (SubcategoryRouter,
            RegionRouter,
            SubregionRouter,
            WarehouseRouter,
            DrinkRouter,
            ItemRouter)


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
async def fakedata_generator(authenticated_client_with_db, test_db_session,
                             simple_router_list, complex_router_list):
    # from tests.data_factory.fake_generator import generate_test_data
    source = simple_router_list + complex_router_list
    test_number = 10
    client = authenticated_client_with_db
    for n, item in enumerate(source):
        router = item()
        schema = router.create_schema
        adapter = TypeAdapter(schema)
        prefix = router.prefix
        test_data = generate_test_data(
            schema, test_number,
            {'int_range': (1, test_number),
             'decimal_range': (0.5, 1),
             'float_range': (0.1, 1.0),
             # 'field_overrides': {'name': 'Special Product'},
             'faker_seed': 42})
        for m, data in enumerate(test_data):
            try:
                # _ = schema(**data)      # валидация данных
                json_data = json.dumps(data)
                adapter.validate_json(json_data)
                assert True
            except Exception as e:
                assert False, f'Error IN INPUT VALIDATION {e}, router {prefix}, example {m}'
            try:
                response = await client.post(f'{prefix}', json=data)
                assert response.status_code == 200, f'||{prefix}, {response.text}'
            except Exception as e:
                assert False, f'{response.status_code=} {prefix=}, error: {e}, example {m}, {response.text}'


@pytest.fixture(scope=scope)
async def fakedata_generator1(authenticated_client_with_db, test_db_session, get_fields_type):
    """
    проходит по списку роутеров и заполняет таблицы данными
    :return:
    :rtype:
    """
    client = authenticated_client_with_db
    counts = example_count
    for key, val in get_fields_type.items():
        for n in range(counts):
            try:
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
            except Exception as e:
                assert False, f'fakedata_generator {e} {route} {response.text}'


@pytest.fixture(scope=scope)
def routers_get_one() -> List[str]:
    """ список роутеров GET get_by_id"""
    return [x.path for x in get_routers('GET') if x.name == 'get_one']


@pytest.fixture(scope=scope)
def routers_get_all() -> List[str]:
    """ список роутеров GET get_all"""
    return [x.path for x in get_routers('GET') if x.name == 'get']


@pytest.fixture(scope=scope)
def real_routers_get_all() -> List[APIRoute]:
    """ список роутеров GET get_all"""
    return [x for x in get_routers('GET') if x.name == 'get']


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
    st = settings_db
    return (f"postgresql+psycopg_async://{st.POSTGRES_USER}:"
            f"{st.POSTGRES_PASSWORD}@{st.POSTGRES_HOST}:{st.PG_PORT}/{st.POSTGRES_DB}")


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
        # await conn.run_sync(Base.metadata.drop_all, checkfirst=False, cascade=True)
        await conn.execute(text("DROP SCHEMA public CASCADE;"))
        await conn.execute(text("CREATE SCHEMA public;"))
        await conn.execute(text("GRANT ALL ON SCHEMA public TO public;"))
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

    async def override_get_mongodb():
        return test_mongodb

    async def override_get_database():
        return test_mongodb.database

    # override_app_dependencies[app.dependency_overrides] = get_test_db
    app.dependency_overrides[get_db] = get_test_db
    app.dependency_overrides[get_mongodb] = override_get_mongodb
    app.dependency_overrides[get_database] = override_get_database

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
