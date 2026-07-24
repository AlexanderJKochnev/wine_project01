# app.core.admin.config.py
"""
starlette-admin
"""

from fastapi import FastAPI
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import UserAdminView
from app.auth.models import User


def create_and_mount_admin(app: FastAPI, async_engine) -> Admin:
    """Полностью инициализирует и монтирует админку.
    Вызывается строго внутри lifespan, когда AsyncEngine гарантированно запущен."""

    admin = Admin(
        engine=async_engine,  # Передаем уже рабочий, запущенный движок
        title="Управление системой", base_url="/admin", auth_provider=AdminAuthProvider()
    )

    # Ваша договоренность: ниже только регистрация вьюх из views.py
    admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))

    # Динамически монтируем админку в runtime
    admin.mount_to(app)

    return admin
