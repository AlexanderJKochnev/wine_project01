# app/admin/auth.py
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

#  from starlette.responses import RedirectResponse
from app.auth.repository import UserRepository
# from app.auth.utils import verify_token
from app.core.config.database.db_async import AsyncSessionLocal
from app.core.config.project_config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            return False

        async with AsyncSessionLocal() as session:
            user_repo = UserRepository()
            user = await user_repo.authenticate(username, password, session)

            if user and user.is_superuser:
                # Создаем токен для админки
                expire = datetime.now(timezone.utc) + timedelta(hours=1)
                token = jwt.encode({"sub": username, "superuser": True, "exp": expire},
                                   settings.SECRET_KEY, algorithm=settings.ALGORITHM,)
                request.session.update({"admin_token": token})

                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("admin_token")
        if not token:
            return False

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            # payload = jwt.decode(token, "admin-secret-key", algorithms=["HS256"])
            username = payload.get("sub")
            is_superuser = payload.get("superuser")

            if not username or not is_superuser:
                return False

            # Проверяем, что пользователь все еще суперпользователь
            async with AsyncSessionLocal() as session:
                user_repo = UserRepository()
                user = await user_repo.get_by_field("username", username, session)
                if not user or not user.is_superuser or not user.is_active:
                    return False

            return True
        except JWTError:
            return False


# authentication_backend = AdminAuth(secret_key="admin-secret-key")
authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
