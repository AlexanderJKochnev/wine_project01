# tests/test_routers.py
import pytest
# from fastapi import status
# from sqlalchemy import text
# from sqlalchemy.exc import SQLAlchemyError
from app.support.color.router import ColorRouter as Router


pytestmark = pytest.mark.asyncio


async def test_color_create_get_one(authenticated_client_with_db):
    prefix = Router().prefix
    data = {'name': 'Red', 'name_ru': 'Красный'}  # , 'description': 'rrr', 'description_ru': 'fff'}
    ac = authenticated_client_with_db
    response = await ac.post(f'{prefix}', json=data)
    assert response.status_code == 200
    result = response.json()

    for key, val in data.items():
        assert result.get(key) == val, f'{key} {val}'
    # item_id = result.get('id')
    # response = await ac.get(f'{prefix}')
    assert response.status_code == 201, result
