# app/dependencies.py
from functools import lru_cache
from typing import Any, Awaitable, Callable, Dict, Optional

from app.core.config.database.redis_async import RedisManager
from app.core.repositories.clickhouse_repository import ClickHouseRepositoryFactory
from clickhouse_connect.driver.asyncclient import AsyncClient as ClickAsyncClient
from redis.asyncio import Redis as AsyncRedis
from fastapi import Request
# from app.core.services.translate_service import TranslationService
# from app.core.repositories.clickhouse_repository import ClickHouseRepositoryFactory
from app.core.utils.translation_utils import fill_missing_translations


@lru_cache()
async def get_ch_client(request: Request) -> ClickAsyncClient:
    """Получение асинхронного клиента ClickHouse."""
    client = request.app.state.ch_client
    if client is None:
        raise RuntimeError("ClickHouse client not initialized")
    return client  # ← это уже AsyncClient, не корутина!


async def get_clickhouse_repository_factory(request: Request
                                            # client: ClickAsyncClient = Depends(get_ch_client)
                                            ) -> ClickHouseRepositoryFactory:
    """ Фабрика для работы с любыми таблицами.
        пример:
        repo_factory: ClickHouseRepositoryFactory = Depends(get_clickhouse_repository_factory)
        repo = repo_factory.for_table('images_metadata')
    """
    return request.app.state.ch_repo_factory
    # return ClickHouseRepositoryFactory(client)


def get_translator_func() -> Callable[[Dict[str, Any], Optional[bool]], Awaitable[Dict[str, Any]]]:
    return fill_missing_translations


async def get_translation_service(request: Request):
    service_manager = request.app.state.service_manager
    return await service_manager.get("translation")


def get_redis_client(request: Request) -> AsyncRedis:
    """Отдать чистый асинхронный клиент Redis в эндпоинт."""
    redis_manager = request.app.state.redis_manager
    return redis_manager.get_async_client()
