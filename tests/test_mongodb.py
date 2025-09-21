import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from app.mongodb.config import mongodb
from tests.config import settings_db

pytestmark = pytest.mark.asyncio


async def test_direct_mongo_connection():
    """Прямое тестирование подключения к MongoDB"""
    try:
        mongo_url = settings_db.mongo_url
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=500)
        # Проверяем подключение
        await client.admin.command('ping')
        client.close()
        return True
    except Exception as e:
        print(f"Direct connection failed: {e}")
        assert False, f"{e} {mongo_url=}"


async def test_mongodb_connection():
    """Прямое тестирование подключения к MongoDB"""
    from app.mongodb.config import MongoDB, get_mongodb, get_database
    try:
        mongo_url = settings_db.mongo_url
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=500)
        # Проверяем подключение
        await client.admin.command('ping')
        client.close()
    except Exception as e:
        print(f"Direct connection failed: {e}")
        assert False, f"{e} {mongo_url=}"
    try:
        test_mongo = MongoDB()
        test_url = settings_db.mongo_url
        # test_url = f'{settings_db.mongo_url}/test_db'
        await test_mongo.connect(test_url, "test_db")
        yield test_mongo
        await test_mongo.disconnect()
    except Exception as e:
        assert False, e

async def test_app_mongo_connection(authenticated_client_with_db, test_db_session, test_mongodb):
    """Тестирование подключения через приложение"""
    from app.mongodb.config import (MongoDB)
    from app.mongodb.router import get_mongodb
    try:
        client = authenticated_client_with_db
        prefix = 'mongodb/images/'
        response = await client.get(prefix)
        assert response.status_code == 200, response.text
    except Exception as e:
        # print(f"App connection failed: {e}")
        connected = False

        assert connected, f"Подключение через приложение не удалось: {e}"


@pytest.mark.skip
async def test_mongo_health_endpoint(authenticated_client_with_db, test_db_session):
    """Тестирование health endpoint"""
    client = authenticated_client_with_db
    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    print(f"Health response: {data}")

    # Проверяем структуру ответа

    assert "mongo_connected" in data
    assert data["mongo_connected"], data
    assert "status" in data
    assert data['status'] == 'healthy', "соединение с MongoDb установлено, но не работает должным образом"


@pytest.mark.skip
async def test_mongo_connection_flow():
    """Полный тест потока подключения"""
    # Проверяем, что изначально клиент None
    assert mongodb.client is None

    # Подключаемся
    await connect_to_mongo()

    # Проверяем, что клиент создан
    assert mongodb.client is not None
    assert mongodb.database is not None

    # Проверяем, что можем выполнять операции
    try:
        collections = await mongodb.database.list_collection_names()
        print(f"Collections: {collections}")
        can_operate = True
    except Exception as e:
        print(f"Operation failed: {e}")
        can_operate = False

    # Отключаемся
    await close_mongo_connection()

    # Проверяем, что отключились
    assert mongodb.client is None

    assert can_operate, "Не удалось выполнить операции с MongoDB"


async def test_mongo_authentication():
    """Тестирование аутентификации с разными credentials"""
    test_cases = [{"url": settings_db.mongo_url, "should_work": True},
                  {"url": f"mongodb://wrong:wrong@mongodb:{settings_db.MONGO_OUT_PORT}", "should_work": False},
                  {"url": "mongodb://mongodb:27017", "should_work": False},  # без аутентификации
                  ]

    for case in test_cases:
        try:
            client = AsyncIOMotorClient(case["url"], serverSelectionTimeoutMS=3000)
            await client.admin.command('ping')
            client.close()
            if not case["should_work"]:
                assert False
            else:
                assert True
        except Exception:
            if case["should_work"]:
                assert False

    assert True


async def test_connection_timeout():
    """Тестирование таймаутов подключения"""
    try:
        # Очень короткий таймаут для теста
        client = AsyncIOMotorClient(
            settings_db.mongo_url, serverSelectionTimeoutMS=100  # 100ms - очень коротко
        )
        await client.admin.command('ping')
        client.close()
        print("Connection with short timeout - SUCCESS")
        assert True
    except Exception as e:
        result = f"Connection with short timeout - FAILED (expected): {e}"
        assert False, result
