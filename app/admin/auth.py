# app/admin/auth.py
import logging
from datetime import datetime, timedelta

from jose import jwt, JWTError
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

#  from starlette.responses import RedirectResponse
from app.auth.repository import UserRepository
# from app.auth.utils import verify_token
from app.core.config.database.db_async import AsyncSessionLocal
from app.core.config.project_config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

        if not username or not password:
            logger.warning("Login failed: missing username or password")
            return False

        async with AsyncSessionLocal() as session:
            user_repo = UserRepository()
            user = await user_repo.authenticate(username, password, session)

            if user and user.is_superuser:
                # Создаем токен для админки
                expire = datetime.utcnow() + timedelta(hours=1)
                token = jwt.encode({"sub": username, "superuser": True, "exp": expire},
                                   settings.SECRET_KEY, algorithm=settings.ALGORITHM,)
                request.session.update({"admin_token": token})
                logger.info(f"Admin login successful for {username}")
                return True
        logger.warning("Login failed: invalid credentials or not superuser")
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        logger.info("Admin logged out")
        return True

    async def authenticate(self, request: Request) -> bool:
        logger.info("Authenticating admin request")
        token = request.session.get("admin_token")
        if not token:
            logger.warning("No admin_token in session")
            return False

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            # payload = jwt.decode(token, "admin-secret-key", algorithms=["HS256"])
            username = payload.get("sub")
            is_superuser = payload.get("superuser")

            if not username or not is_superuser:
                logger.warning("Token invalid: missing sub or superuser")
                return False

            # Проверяем, что пользователь все еще суперпользователь
            async with AsyncSessionLocal() as session:
                user_repo = UserRepository()
                user = await user_repo.get_by_field("username", username, session)
                if not user or not user.is_superuser or not user.is_active:
                    logger.warning("User no longer valid for admin access")
                    return False

            logger.info("Admin authentication successful")
            return True
        except JWTError:
            return False


# authentication_backend = AdminAuth(secret_key="admin-secret-key")
authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
