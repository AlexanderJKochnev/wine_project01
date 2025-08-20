# tests/test_fastapi2.py
import pytest
# from fastapi import status
# from sqlalchemy import select
# from app.support.color.model import Color
from fastapi.security import OAuth2PasswordRequestForm

pytestmark = pytest.mark.asyncio


async def test_get(authenticated_client_with_db1, test_db_session):
    for key in ('docs', 'redoc'):
        response = await authenticated_client_with_db1.get(f'/{key}')
        assert response.status_code == 200


@pytest.mark.skip
async def test_login(unauthenticated_client_with_db, super_user, test_db_session):
    ac = unauthenticated_client_with_db
    login_data = {key: val for key, val in super_user.items() if key in ('username', 'password')}
    form_data = OAuth2PasswordRequestForm(username=login_data.get('username'), password=login_data.get('password'))
    print(f'{form_data=}')
    response = await ac.post("/auth/login/", data=form_data)

    if response.status_code == 307:
        # Получаем URL из заголовка Location
        redirect_url = response.headers.get('location')
        print(f'{redirect_url=}')
        response = await ac.post(redirect_url, data=form_data)
        print(f'{response.status_code=}')
    assert response.status_code == 200
