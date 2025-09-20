# app/mongodb/config.py
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends  # NOQA: F401
# import os

MONGO_URL = "mongodb://admin:admin@mongodb:27017"
DATABASE_NAME = "files_db"


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    if mongodb.client is None:
        mongodb.client = AsyncIOMotorClient(MONGO_URL)
        mongodb.database = mongodb.client[DATABASE_NAME]
        print("Connected to MongoDB")


async def close_mongo_connection():
    if mongodb.client:
        mongodb.client.close()
        mongodb.client = None
        print("Disconnected from MongoDB")


# Dependency для использования в роутерах
async def get_mongo_db():
    if mongodb.client is None:
        await connect_to_mongo()
    return mongodb.database
