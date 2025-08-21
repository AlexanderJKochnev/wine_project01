# tests/test_fastapi2.py
import pytest
pytestmark = pytest.mark.asyncio


async def test_get(authenticated_client_with_db, test_db_session):
    for key in ('docs', 'redoc'):
        response = await authenticated_client_with_db.get(f'/{key}')
        assert response.status_code == 200
