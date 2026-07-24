# app.admin.auth.py
from fastapi import FastAPI
from fastapi_amis_admin.admin import Settings
from fastapi_user_auth.admin import AuthAdminSite
from fastapi_amis_admin.admin.site import AdminSite
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import SQLModel
from loguru import logger
import os

from app.core.config.database.db_config import settings_db


def setup_auth_middleware(app: FastAPI):
    secret_key = settings_db.SECRET_KEY
    app.add_middleware(
        SessionMiddleware,
        secret_key=secret_key,
        session_cookie="admin_session",
        max_age=60 * 60 * 24 * 7,
        same_site="lax",
        https_only=False,
    )


def init_admin(app: FastAPI):
    # setup_auth_middleware(app)

    # ИСХОДНЫЙ КОД ИЗ ДОКУМЕНТАЦИИ, НИЧЕГО НЕ МЕНЯЕМ
    site = AuthAdminSite(
        settings=Settings(database_url_async=settings_db.database_url)
    )
    # site.mount_app(app)

    # 2. Основная админка (AdminSite) с моделями
    admin_site = AdminSite(
        settings=Settings(database_url_async=settings_db.database_url)  # , site_path="/admin"
        # Явно указываем путь
    )

    # Регистрируем модели
    # register_all_models(admin_site)

    admin_site.mount_app(app)

    from app.admin.models import UserAdmin
    admin_site.register_admin(UserAdmin)

    return site
