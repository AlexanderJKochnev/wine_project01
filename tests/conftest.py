# tests/conftest.py

import asyncio
import logging
import pytest
from httpx import ASGITransport, AsyncClient
from app import main
from tests import config
# from app.core.config.database.db_helper import db_help
# from tests.router import router as testrouter


scope = 'session'
logger = logging.getLogger(__name__)


@pytest.fixture(scope=scope)
def event_loop(request):
    """
    Создаём отдельный event loop для всей сессии тестов.
    Это предотвращает ошибку "Event loop is closed".
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    try:
        yield loop
    finally:
        if not loop.is_closed():
            loop.close()


@pytest.fixture(scope=scope)
def base_url():
    return config.base_url_doc


@pytest.fixture(scope=scope)
def super_user():
    return None


@pytest.fixture(scope=scope)
async def logged_in_user_real(super_user):
    """ подстановка пользователя для запуска клиента без моков """
    # test_user = super_user
    app = main.app
    # app.include_router(testrouter)
    # injection test user to app
    # app.dependency_overrides[get_current_user] = lambda: test_user
    # app.dependency_overrides[get_current_active_superuser] = lambda: test_user
    # pp.plugin_injection(app)
    return app


@pytest.fixture(scope=scope)
async def async_test_app(logged_in_user_real,
                         event_loop,
                         base_url,
                         ):
    """ запуск клиента из-вне"""
    async with AsyncClient(
            transport=ASGITransport(app=logged_in_user_real),
            base_url=base_url
    ) as ac:
        # передача управления
        yield ac, logged_in_user_real
        # event_loop.run_until_complete(ac.aclose())

"""
@pytest.fixture(scope=scope)
async def add_router(async_test_app):
    ac, app = async_test_app
"""
