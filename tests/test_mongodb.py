import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.mongodb.config import connect_to_mongo, close_mongo_connection, mongodb
from tests.config import settings_db

pytestmark = pytest.mark.asyncio


async def test_direct_mongo_connection():
    """Прямое тестирование подключения к MongoDB"""
    try:
        mongo_url = settings_db.mongo_url
        # mongo_url = "mongodb://admin:admin@localhost:27027"
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=10000)
        # Проверяем подключение
        await client.admin.command('ping')
        client.close()
        return True
    except Exception as e:
        print(f"Direct connection failed: {e}")
        assert False, f"{e} {mongo_url=}"


async def test_app_mongo_connection():
    """Тестирование подключения через приложение"""
    try:
        # Имитируем запуск приложения
        await connect_to_mongo()
        connected = mongodb.client is not None

        if connected:
            # Дополнительная проверка, что база данных доступна
            db = mongodb.client.get_database("files_db")
            collections = await db.list_collection_names()
            print(f"Available collections: {collections}")

        await close_mongo_connection()
    except Exception as e:
        print(f"App connection failed: {e}")
        connected = False

    assert connected, "Подключение через приложение не удалось"


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
