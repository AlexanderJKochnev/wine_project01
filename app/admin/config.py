# app.core.admin.config.py
"""
starlette-admin
"""

from fastapi import FastAPI
from jinja2 import ChoiceLoader, FileSystemLoader
from starlette_admin.contrib.sqla import Admin

from app.admin.auth import AdminAuthProvider
from app.admin.views import CategoryView, SomeView, UserAdminView
from app.auth.models import User
from app.support import Category
from app.support.vllm.model import TranslateHelper


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

    # 2. ЖЕСТКОЕ РЕШЕНИЕ: Принудительно объединяем кастомный и оригинальный загрузчики
    # Это заставит Jinja2 ВСЕГДА проверять вашу папку первой, даже при 404 и logout
    original_loader = admin.templates.env.loader
    custom_loader = FileSystemLoader("templates")

    # ChoiceLoader сначала ищет файл у вас, а если не находит — берет дефолтный из пакета
    admin.templates.env.loader = ChoiceLoader([custom_loader, original_loader])

    admin.add_view(UserAdminView(User, identity="user", label="Пользователи"))
    admin.add_view(SomeView(TranslateHelper, identity="translatehelper", label="Словарь"))
    admin.add_view(CategoryView(Category, identity="category", label="Категории"))
    admin.mount_to(app)

    return admin
