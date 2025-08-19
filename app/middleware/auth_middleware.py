# app/middleware/auth_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED
# import re


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, exclude_paths=None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/auth/login",
            "/auth/register",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/admin"]

    async def dispatch(self, request: Request, call_next):
        # Проверяем, нужно ли исключить путь
        for path in self.exclude_paths:
            if request.url.path.startswith(path):
                return await call_next(request)

        # Проверяем наличие токена для остальных путей
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=HTTP_401_UNAUTHORIZED,
                content={"detail": "Not authenticated"}
            )

        response = await call_next(request)
        return response

# В app/main.py добавить:
# from app.middleware.auth_middleware import AuthMiddleware
# app.add_middleware(AuthMiddleware)
