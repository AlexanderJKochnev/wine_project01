# app.core.services.vllm_service_manager.py
import asyncio
from datetime import datetime

from loguru import logger

from app.core.services.translate_service import BaseService


class ServiceManager:
    """ Менеджер сервисов с ленивой загрузкой и автовыгрузкой
        корректно закрывает семафоры
        по умолчанию настроен на vllm сервисы
    """

    def __init__(self, idle_timeout_minutes: int = 10):
        self.idle_timeout: int = idle_timeout_minutes
        self._services: dict = {}  # service_type -> instance
        self._last_used: dict = {}  # service_type -> datetime
        self._configs: dict = {}  # service_type -> {"class": Class, "config": {}}
        self._running: bool = False  # флаг работы фоновой очистки
        self._cleanup_task = None  # ссылка на фоновую задачу (чтобы отменить при stop)

        # for cls in BaseService.__subclasses__():
        #     name = cls.__name__.lower().replace('service', '')  # TranslationService → translation
        #     self.register(name, cls)

    def register(self, name: str, cls, config: dict = None):
        """Зарегистрировать тип сервиса"""
        self._configs[name] = {"cls": cls, "config": config or {}}

    async def get(self, name: str):
        """Получить сервис (ленивая загрузка)"""
        if name not in self._services:
            cfg = self._configs[name]
            service = cfg["cls"](config=cfg["config"])
            await service.initialize()
            self._services[name] = service
        self._last_used[name] = datetime.now()
        return self._services[name]

    async def unload(self, name: str):
        """Выгрузить сервис"""
        if name in self._services:
            logger.info(f"🔄 Unloading: {name}")
            await self._services[name].close()
            del self._services[name]
            self._last_used.pop(name, None)
            logger.info(f"✅ Unloaded: {name}")

    async def unload_all(self):
        for name in list(self._services.keys()):
            await self.unload(name)

    async def start(self):
        """Запустить фоновую очистку"""
        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup())
        await asyncio.sleep(0)

    async def stop(self):
        """Остановить и выгрузить всё"""
        self._running = False
        for name in list(self._services.keys()):
            await self.unload(name)

    async def _cleanup(self):
        """Фоновая очистка неиспользуемых сервисов"""
        while self._running:
            await asyncio.sleep(60)
            now = datetime.now()
            for name, last_used in list(self._last_used.items()):
                if (now - last_used).total_seconds() > self.idle_timeout * 60:
                    await self.unload(name)
