# app.core.admin.config.py
"""
starlette-admin
"""

from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import UserAdminView
from app.auth.models import User


def setup_starlette_admin(app: FastAPI, engine) -> Admin:
    """Инициализирует и монтирует админку к FastAPI приложению."""

    admin = Admin(
        engine=engine, title="Управление системой", base_url="/admin", auth_provider=AdminAuthProvider()
    )

    # Регистрируем кастомное представление для модели User
    admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))

    # Монтируем к основному приложению FastAPI
    admin.mount_to(app)

    return admin
