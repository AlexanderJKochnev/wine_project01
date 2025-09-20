import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.mongodb.config import connect_to_mongo, close_mongo_connection, mongodb


class TestMongoDBConnection:
    """Тесты для проверки подключения к MongoDB"""
    
    @pytest.mark.asyncio
    async def test_direct_mongo_connection(self):
        """Прямое тестирование подключения к MongoDB"""
        try:
            client = AsyncIOMotorClient(
                    "mongodb://admin:admin@mongo:27017", serverSelectionTimeoutMS=5000
                    )
            # Проверяем подключение
            await client.admin.command('ping')
            connected = True
            client.close()
        except Exception as e:
            print(f"Direct connection failed: {e}")
            connected = False

        assert connected, "Прямое подключение к MongoDB не удалось"

    @pytest.mark.asyncio
    async def test_app_mongo_connection(self):
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
    
    @pytest.mark.asyncio
    async def test_mongo_health_endpoint(self, client):
        """Тестирование health endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        print(f"Health response: {data}")
        
        # Проверяем структуру ответа
        assert "status" in data
        assert "mongo_connected" in data
        
        return data["mongo_connected"]
    
    @pytest.mark.asyncio
    async def test_mongo_connection_flow(self):
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


@pytest.mark.asyncio
async def test_mongo_connection_integration():
    """Интеграционный тест подключения"""
    # Тестируем разные URL для подключения
    test_urls = ["mongodb://admin:admin@mongodb:27017", "mongodb://admin:admin@localhost:27017",
            # на случай если docker-compose network работает иначе
            "mongodb://admin:admin@host.docker.internal:27017"  # для Docker Desktop
            ]
    
    for url in test_urls:
        try:
            print(f"Testing connection to: {url}")
            client = AsyncIOMotorClient(url, serverSelectionTimeoutMS = 3000)
            await client.admin.command('ping')
            print(f"Successfully connected to: {url}")
            client.close()
            return True
        except Exception as e:
            print(f"Failed to connect to {url}: {e}")
    
    return False