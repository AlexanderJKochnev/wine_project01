from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class FixAmisCookieMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Перехватываем куку авторизации только при запросах к админке
        if request.url.path.startswith("/admin") and "Authorization" in request.cookies:
            cookie_val = request.cookies["Authorization"]

            # Если библиотека ошибочно передала токен с приставкой bearer
            if cookie_val.lower().startswith("bearer "):
                # Очищаем токен от префикса и кавычек
                clean_token = cookie_val[7:].strip().strip('"').strip("'")

                # Модифицируем "сырые" ASGI заголовки в текущем scope запроса
                headers = dict(request.scope["headers"])

                # Пересобираем строку заголовка Cookie, убирая слово bearer
                all_cookies = []
                for k, v in request.cookies.items():
                    if k == "Authorization":
                        all_cookies.append(f'{k}="{clean_token}"')
                    else:
                        all_cookies.append(f'{k}={v}')

                new_cookie_header = "; ".join(all_cookies)

                # Записываем исправленную куку обратно в контекст запроса
                headers[b"cookie"] = new_cookie_header.encode("latin-1")
                request.scope["headers"] = list(headers.items())

        response = await call_next(request)
        return response
