# app.admin.auth.py
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.auth import AuthProvider
from starlette_admin.exceptions import LoginFailed

from app.auth.models import User
from app.auth.repository import UserRepository
from app.core.config.database.db_async import get_db


class AdminAuthProvider(AuthProvider):
    async def login(
        self, username: str, password: str,
        remember_me: bool, request: Request, response: Response,
    ) -> Response:
        # Получаем данные из стандартной HTML-формы админки
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        repo = UserRepository
        session = get_db()
        user = await repo.authenticate(username, password, session)
        if user and user.is_superuser:
            user_data = {"username": username, "role": "superuser"}
            # Записываем данные в сессию FastAPI
            request.session.update({"admin_user": user_data})
            # Возвращаем request, это сигнализирует starlette-admin об успешном входе
            return response

        raise LoginFailed("Неверное имя пользователя или пароль или прав недостаточно")
    
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
    
    async def is_authenticated(self, request: Request) -> bool:
        return "admin_user" in request.session