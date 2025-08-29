# tests/test_create.py
"""
    валидация генерируемых тестовых данных
    проверка метода POST
    новые методы добавляются автоматически
"""

import pytest
from app.core.schemas.base import ListResponse

pytestmark = pytest.mark.asyncio


async def test_input_validation(authenticated_client_with_db,
                                test_db_session,
                                routers_get_all,
                                fakedata_generator):
    client = authenticated_client_with_db