# app/core/config/database/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    try:
        mongodb.client = AsyncIOMotorClient(
                settings.MONGODB_URL, maxPoolSize = 10, minPoolSize = 5
                )
        mongodb.database = mongodb.client[settings.MONGO_DB_NAME]
        logger.info("Connected to MongoDB successfully")
        
        # Проверяем соединение
        await mongodb.database.command("ping")
        logger.info("MongoDB ping successful")
    
    except Exception as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        logger.info("MongoDB connection closed")


def get_mongo_db():
    return mongodb.database