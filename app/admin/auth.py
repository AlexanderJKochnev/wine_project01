# app.admin.auth.py

from fastapi import FastAPI
from fastapi_amis_admin.admin import Settings
from fastapi_user_auth.admin import AuthAdminSite
import os
from starlette.middleware.sessions import SessionMiddleware
from app.core.config.database.db_config import settings_db
from app.auth.repository import UserRepository
from app.auth.models import User

# site = AuthAdminSite(
#     settings=Settings(database_url_async=settings_db.database_url)
# )
# auth = site.auth


# ========== 1. MIDDLEWARE ДЛЯ СЕССИЙ ==========
def setup_auth_middleware(app: FastAPI):
    """Добавляет SessionMiddleware для хранения данных о входе"""
    secret_key = settings_db.SECRET_KEY or os.urandom(32).hex()
    app.add_middleware(
        SessionMiddleware, secret_key=secret_key, session_cookie="admin_session", max_age=60 * 60 * 24 * 7,
        # 7 дней
        same_site="lax", https_only=False, )


# ========== 2. ИНИЦИАЛИЗАЦИЯ АДМИНКИ С АВТОРИЗАЦИЕЙ ==========
def init_admin(app: FastAPI):
    """Создает и настраивает AuthAdminSite с авторизацией"""
    # Добавляем middleware для сессий
    setup_auth_middleware(app)

    # Создаем админку с авторизацией
    site = AuthAdminSite(
        settings=Settings(
            database_url_async=settings_db.database_url
        )
    )

    # Монтируем к приложению (без аргументов)
    site.mount_app(app)

    # Создаем таблицы и тестового пользователя при старте
    @app.on_event("startup")
    async def startup():
        # Создаем таблицы для auth
        from sqlmodel import SQLModel
        await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)

        # Создаем тестового администратора
        await site.auth.create_role_user('admin')  # Пароль по умолчанию: 'admin'
        # await site.auth.create_role_user('vip')  # Раскомментируйте, если нужен vip
        print("✅ Админка с авторизацией настроена. Логин: admin, пароль: admin")

    return site
