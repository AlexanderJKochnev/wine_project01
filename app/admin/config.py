# app.core.admin.config.py
"""
starlette-admin
"""

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import UserAdminView
from app.auth.models import User


# 🛠 СОЗДАЕМ ЗАГЛУШКУ ДВИЖКА (чтобы избежать ошибки при старте)
# Он не делает сетевых запросов и нужен только для инициализации класса Admin
mock_engine = create_async_engine("sqlite+aiosqlite:///:memory:")

admin = Admin(
    engine=mock_engine,
    title="Управление системой",
    base_url="/admin",
    auth_provider=AdminAuthProvider()
)

# Сразу регистрируем представления (им движок на этом этапе не нужен)
admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))


def init_admin_scopes(app: FastAPI):
    """Монтирует роуты админки к приложению.
    Вызывается глобально в main.py до старта lifespan."""
    admin.mount_to(app)


def connect_admin_db(async_engine):
    """Динамически подключает запущенный асинхронный движок к админке.
    Вызывается строго ВНУТРИ lifespan после инициализации DatabaseManager."""
    admin.configure(engine=async_engine)
