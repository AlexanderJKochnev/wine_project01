# app.admin.auth.py

import os
from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.admin.site import AdminSite

from app.core.config.database.db_config import settings_db as app_settings
from app.core.config.database.db_async import get_db as get_async_session
from app.auth.models import User
from app.auth.repository import UserRepository


# ========== 1. MIDDLEWARE ДЛЯ СЕССИЙ ==========
def setup_auth_middleware(app: FastAPI):
    secret_key = app_settings.secret_key or os.urandom(32).hex()
    app.add_middleware(
        SessionMiddleware, secret_key=secret_key, session_cookie="admin_session", max_age=60 * 60 * 24 * 7,
        same_site="lax", https_only=False, )


# ========== 2. КЛАСС АВТОРИЗАЦИИ ==========
class AdminAuth:
    """
    Класс авторизации для fastapi-amis-admin.
    AdminSite принимает объект auth с методами get_current_user и login.
    """

    def __init__(self):
        self.login_path = "/admin/auth/login"
        self.logout_path = "/admin/auth/logout"

    async def get_current_user(self, request: Request) -> dict | None:
        """Проверяет авторизацию пользователя"""
        user_id = request.session.get("user_id")
        if not user_id:
            return None

        async for session in get_async_session():
            user = await session.get(User, user_id)
            if user and user.is_superuser and user.is_active:
                return {"id": user.id, "username": user.username, "avatar": None, }
        return None

    async def login(self, request: Request, username: str, password: str) -> dict | None:
        """Аутентификация пользователя"""
        async for session in get_async_session():
            user = await UserRepository.authenticate(username, password, session)
            if user and user.is_superuser and user.is_active:
                request.session["user_id"] = user.id
                return {"id": user.id, "username": user.username, }
        return None

    async def logout(self, request: Request):
        """Выход из системы"""
        request.session.clear()
        return {"status": "ok"}


# ========== 3. ИНИЦИАЛИЗАЦИЯ АДМИНКИ ==========
def init_admin(app: FastAPI):
    """Создает и настраивает AdminSite с авторизацией"""
    # Добавляем middleware для сессий
    setup_auth_middleware(app)

    # Создаем объект авторизации
    auth = AdminAuth()

    # Настройки админки
    settings = Settings(
        database_url_async=app_settings.database_url,  # 🔑 КЛЮЧЕВОЙ МОМЕНТ: передаем auth в Settings
        auth=auth, )

    # Создаем AdminSite с указанием пути
    admin_site = AdminSite(
        settings=settings, site_path="/admin"
    )

    # Монтируем к приложению
    admin_site.mount_app(app)

    return admin_site
