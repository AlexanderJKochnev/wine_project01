# app.admin.auth.py

from fastapi import FastAPI
from fastapi_amis_admin.admin import Settings
from fastapi_user_auth.admin import AuthAdminSite

from app.core.config.database.db_config import settings_db

site = AuthAdminSite(
    settings=Settings(database_url_async=settings_db.database_url)
)
auth = site.auth