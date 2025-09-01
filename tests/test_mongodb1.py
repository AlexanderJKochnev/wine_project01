# tests/test_mongodb1.py
import pytest
from motor.motor_asyncio import AsyncIOMotorClient

pytestmark = pytest.mark.asyncio


async def test_mongodb_connection_string(mongo_url):
    """Тест строки соединения с MongoDB"""
    client = None
    try:
        client = AsyncIOMotorClient('localhost:27017',
                                    username='admin',
                                    password='password',
                                    authSource='admin',
                                    replicaSet='rs0',
                                    maxPoolSize=10,
                                    minPoolSize=5,
                                    directConnection=True)
        # Проверяем соединение
        await client.admin.command('ping')
        assert True
    except Exception as e:
        pytest.fail(f'Ошибка соединения с MongoDB: {e}')
    finally:
        if client:
            client.close()


async def test_mongo_client(mongo_client):
    """Тест клиента MongoDB"""
    try:
        database = mongo_client["myapp_mongodb"]
        # Проверяем соединение
        await database.command("ping")
        assert True
    except Exception as e:
        pytest.fail(f'Ошибка соединения с MongoDB: {e}')


async def test_mongo_session(mongo_client):
    """Тест работы с сессиями MongoDB"""
    try:
        database = mongo_client["myapp_mongodb"]
        # Важно: создаем сессию и работаем в контексте
        async with await mongo_client.start_session() as session:
            # Можно просто проверить ping в сессии
            await database.command("ping", session=session)
            # Или сделать транзакцию для теста
            async with session.start_transaction():
                test_collection = database["test_collection"]
                await test_collection.insert_one(
                    {"test": "data"}, session=session
                )
                # Проверяем, что данные вставлены
                result = await test_collection.find_one(
                    {"test": "data"}, session=session
                )
                assert result is not None

        assert True

    except Exception as e:
        pytest.fail(f'Ошибка работы с сессией MongoDB: {e}')


async def test_mongo_transaction(mongo_client):
    """Тест транзакций MongoDB"""
    database = mongo_client["myapp_mongodb"]
    test_collection = database["test_collection"]

    try:
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                # Вставляем данные в транзакции
                await test_collection.insert_one(
                    {"transaction": "test", "value": 1}, session=session
                )
                # Проверяем, что данные доступны в транзакции
                doc = await test_collection.find_one(
                    {"transaction": "test"}, session=session
                )
                assert doc is not None
                assert doc["value"] == 1
        # После коммита транзакции проверяем, что данные сохранились
        doc_after = await test_collection.find_one({"transaction": "test"})
        assert doc_after is not None
    except Exception as e:
        pytest.fail(f'Ошибка транзакции MongoDB: {e}')
    finally:
        # Очищаем тестовые данные
        await test_collection.delete_many({"transaction": "test"})


