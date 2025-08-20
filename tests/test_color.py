# tests/test_color.py
import pytest
from fastapi import status
# from app.core.config.project_config import settings
# from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.asyncio


async def test_get_color_authenticated(authenticated_client):
    """Тест получения цветов с аутентификацией"""
    response = await authenticated_client.get("/colors/")  # , follow_redirects=True)
    """if response.status_code == 307:
        # Получаем URL из заголовка Location
        print(f"Redirect location: {response.headers.get('location')}")
        redirect_url = response.headers.get('location')
        response = await authenticated_client.get(redirect_url)"""
    assert response.status_code == status.HTTP_200_OK


def test_get_color_authenticated_sync(sync_authenticated_client):
    response = sync_authenticated_client.get("/colors/")
    assert response.status_code == status.HTTP_200_OK
