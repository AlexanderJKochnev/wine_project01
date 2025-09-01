# app/core/config/database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config.database.mongo_config import settings
# import logging

# logger = logging.getLogger(__name__)


async def mongo_client(host: str = 'localhost',
                       port: int = settings.MONGODB_PORT,
                       username: str = settings.MONGODB_USER_NAME,
                       password: str = settings.MONGODB_USER_PASSWORD,
                       authSource: str = 'admin',
                       replicaSet: str = 'rs0',
                       maxPoolSize: int = 10,
                       minPoolSize: int = 5,
                       directConnection: bool = True,
                       database: str = settings.MONGODB_DATABASE):
    try:
        client = AsyncIOMotorClient(f'{host}:{port}',
                                    username=username,
                                    password=password,
                                    authSource=authSource,
                                    replicaSet=replicaSet,
                                    maxPoolSize=maxPoolSize,
                                    minPoolSize=minPoolSize,
                                    directConnection=directConnection)
        # Проверяем соединение
        await client.admin.command('ping')
        yield client
    except Exception as e:
        print(f'Ошибка соединения с MongoDB: {e}')
    finally:
        if client:
            client.close()


async def get_mongodb(mongo_database: str = settings.MONGODB_DATABASE, **kwargs):
    client = mongo_client(**kwargs)
    async with await client.start_session():
        yield client[f'{mongo_database}']
# ===============================


class MongoDB():
    """ дать описание """
    def __init__(self, *args,
                 host: str = 'localhost',
                 port: int = settings.MONGODB_PORT,
                 username: str = settings.MONGODB_USER_NAME,
                 password: str = settings.MONGODB_USER_PASSWORD,
                 authSource: str = 'admin',
                 replicaSet: str = 'rs0',
                 maxPoolSize: int = 10,
                 minPoolSize: int = 5,
                 directConnection: bool = True,
                 database: str = settings.MONGODB_DATABASE):
        self.client: AsyncIOMotorClient = None
        self.database: str = database
        self.motorini: dict = locals().copy()
        h = self.motorini.pop('host', '')
        p = self.motorini.pop('port', '')
        self.host: dict = f'{h}:{p}'

    def __get_client__(self, motorini: dict):
        self.client = AsyncIOMotorClient(self.host)

    async def get_client(self):
        try:
            client = self.client
            await client.admin.command('ping')
            yield client
        except Exception as e:
            print(f'Ошибка соединения с MongoDB: {e}')
        finally:
            if client:
                client.close()

    async def get_mongo(self):
        async with await self.get_client.start_session():
            yield self.client[f'{self.database_name}']


mongodb = MongoDB()
