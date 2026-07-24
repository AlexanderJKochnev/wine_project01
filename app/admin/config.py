# app.core.admin.config.py
"""
starlette-admin
"""

from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import UserAdminView
from app.auth.models import User


def setup_starlette_admin(app: FastAPI, async_engine) -> Admin:
    """Инициализирует админку, принимая асинхронный AsyncEngine."""

    admin = Admin(
        engine=async_engine,  # Передаем ваш асинхронный engine
        title="Управление системой", base_url="/admin",
        serve_plugins_locally=True,
        templates_dir = "templates",  # Указывает на вашу папку с измененным layout.html
        statics_dir = "static",  # Указывает на папку со скачанными CSS/JS файлами
        auth_provider=None  # AdminAuthProvider()
    )

    admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))
    admin.mount_to(app)

    return admin
