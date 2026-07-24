# app.admin.auth.py
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed

from app.auth.models import User
from app.auth.repository import UserRepository
from app.core.config.database.db_async import get_db


class AdminAuthProvider(AuthProvider):
    def setup_admin(self, admin) -> None:
        """Обязательный абстрактный метод для конфигурации ролей/прав внутри админки.
        Если кастомная логика не требуется, оставляем его пустым."""
    async def login(self, username: str, password: str, remember_me: bool, request: Request) -> dict:
        repo = UserRepository
        session: AsyncSession = get_db()
        user: Optional[User] = await repo.authenticate(username, password, session)
        if user and user.is_superuser:
            user_data = {"username": username, "role": "superuser"}
            request.session.update({"admin_user": user_data})
            return user_data
        raise LoginFailed("Неверное имя пользователя или пароль или прав недостаточно")

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def is_authenticated(self, request: Request) -> bool:
        # Проверка флага сессии при каждом переходе по страницам панели
        return "admin_user" in request.session
