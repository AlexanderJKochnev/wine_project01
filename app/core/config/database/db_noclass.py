# app/core/config/database/no_class.py
# если db_helper затупит
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.config.database.db_config import settings_db

""" simple way """
DATABASE_URL = settings_db.database_url
engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
