# app.core.admin.config.py
"""
starlette-admin
"""

from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import SomeView, UserAdminView
from app.auth.models import User
from app.support import Category


def setup_starlette_admin(app: FastAPI, async_engine) -> Admin:
    """Инициализирует админку, принимая асинхронный AsyncEngine."""

    admin = Admin(
        engine=async_engine,  # Передаем ваш асинхронный engine
        title="Админ панель", base_url="/panel",
        templates_dir="templates",  # Указывает на вашу папку с измененным layout.html
        statics_dir="statics",  # Указывает на папку со скачанными CSS/JS файлами
        auth_provider=AdminAuthProvider(),
        route_name="admin"
    )

    admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))
    admin.add_view(SomeView(User, identity="another", label="Категории"))
    admin.mount_to(app)

    return admin
