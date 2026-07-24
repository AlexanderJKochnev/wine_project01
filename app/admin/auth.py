# app.admin.auth.py
from fastapi import FastAPI
from fastapi_amis_admin.admin import Settings
from fastapi_user_auth.admin import AuthAdminSite
from starlette.middleware.sessions import SessionMiddleware
from sqlmodel import SQLModel
import os

from app.core.config.database.db_config import settings_db


def setup_auth_middleware(app: FastAPI):
    secret_key = settings_db.SECRET_KEY or os.urandom(32).hex()
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
    site.mount_app(app)

    @app.on_event("startup")
    async def startup():
        # СОЗДАЁМ ТАБЛИЦЫ КАК В ДОКУМЕНТАЦИИ
        # await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)
        # СОЗДАЁМ ПОЛЬЗОВАТЕЛЕЙ КАК В ДОКУМЕНТАЦИИ
        from fastapi_user_auth.auth.models import Role, CasbinRule, LoginHistory
        from sqlalchemy import MetaData

        # Собираем все таблицы auth в один metadata
        auth_metadata = MetaData()
        for model in [Role, CasbinRule, LoginHistory]:
            model.__table__.metadata = auth_metadata
        logger.info(auth_metadata)
        print('----------------------------------------------------')
        # Создаём их в базе данных
        await site.db.async_run_sync(auth_metadata.create_all, is_session=False)

        await site.auth.create_role_user('admin')
        await site.auth.create_role_user('vip')
        print("✅ Админка настроена. Логин: admin, пароль: admin")

    return site
