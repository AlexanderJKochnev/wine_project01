# app/support/parser/orchestrator.py

import asyncio
from sqlalchemy import select
from typing import Optional, List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.support.parser.model import Registry, Code, Status
from app.support.parser.repository import RegistryRepository, CodeRepository, StatusRepository
# from app.core.repositories.sqlalchemy_repository import Repository
from sqlalchemy.ext.asyncio import AsyncSession


class ParserOrchestrator:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_default_registry(self) -> Registry:
        """Создаёт или возвращает регистр по умолчанию."""
        default_url = "https://reestrinform.ru/federalnyi-reestr-alkogolnoi-produktcii.html"
        default_shortname = "reestrinform_default"

        registry = await RegistryRepository.get_by_fields(
            {"url": default_url}, Registry, self.session
        )
        if not registry:
            # Получаем статус 'new'
            status_new = await StatusRepository.get_by_fields(
                {"status": "new"}, Status, self.session
            )
            if not status_new:
                raise RuntimeError("Статус 'new' не найден в базе")

            registry = Registry(
                shortname=default_shortname,
                url=default_url,
                status_id=status_new.id,
                base_path="https://reestrinform.ru/federalnyi-reestr-alkogolnoi-produktcii/",
                link_tag="a",
                link_attr="href",
                parent_selector=None,
                timeout=10,
            )
            registry = await RegistryRepository.create(registry, Registry, self.session)
        return registry

    async def fetch_html(self, url: str, timeout: int = 10) -> str:
        """Асинхронно загружает HTML."""
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def extract_links_sync(self, html: str, base_url: str, base_path: str,
                           link_tag: str = "a", link_attr: str = "href",
                           parent_selector: Optional[str] = None) -> List[str]:
        """Синхронная функция парсинга (выполняется в executor)."""
        soup = BeautifulSoup(html, "html.parser")

        container = soup.select_one(parent_selector) if parent_selector else soup
        if not container:
            return []

        links = []
        for tag in container.find_all(link_tag):
            href = tag.get(link_attr)
            if not href:
                continue
            full_url = urljoin(base_url, href)
            if not full_url.startswith(base_path):
                continue
            parsed = urlparse(full_url)
            clean_url = parsed._replace(query='', fragment='').geturl()
            links.append(clean_url)

        return list(dict.fromkeys(links))  # dedup

    async def parse_and_save_codes(self, registry: Registry) -> List[Code]:
        """Парсит ссылки и сохраняет в Code."""
        html = await self.fetch_html(registry.url, registry.timeout or 10)

        # Выполняем синхронный парсинг в потоке, чтобы не блокировать event loop
        loop = asyncio.get_event_loop()
        links = await loop.run_in_executor(
            None,
            self.extract_links_sync,
            html,
            registry.url,
            registry.base_path or registry.url,
            registry.link_tag or "a",
            registry.link_attr or "href",
            registry.parent_selector,
        )

        # Получаем статус 'new'
        status_new = await StatusRepository.get_by_fields(
            {"status": "new"}, Status, self.session
        )
        if not status_new:
            raise RuntimeError("Статус 'new' не найден")

        saved_codes = []
        for url in links:
            # Пытаемся найти существующую запись по url
            existing = await CodeRepository.get_by_fields({"url": url}, Code, self.session)
            if existing:
                continue

            # Извлекаем код из URL (последний сегмент без расширения)
            path = urlparse(url).path
            code = path.strip("/").split("/")[-1]
            if code.endswith(".html"):
                code = code[:-5]

            new_code = Code(
                code=code,
                url=url,
                registry_id=registry.id,
                status_id=status_new.id,
            )
            new_code = await CodeRepository.create(new_code, Code, self.session)
            saved_codes.append(new_code)

        return saved_codes

    async def run(self, shortname: Optional[str] = None, url: Optional[str] = None) -> dict:
        await self.ensure_statuses_exist(self.session)

        # Получаем ID статуса "completed" для сравнения
        status_completed = await StatusRepository.get_by_fields(
            {"status": "completed"}, Status, self.session
        )
        completed_status_id = status_completed.id if status_completed else None

        registry: Optional[Registry] = None

        if shortname:
            stmt = select(Registry).where(Registry.shortname == shortname)
            result = await self.session.execute(stmt)
            registry = result.scalar_one_or_none()
        elif url:
            stmt = select(Registry).where(Registry.url == url)
            result = await self.session.execute(stmt)
            registry = result.scalar_one_or_none()

        if not registry:
            # Ищем первую запись, у которой status_id != completed_status_id
            stmt = select(Registry)
            if completed_status_id is not None:
                stmt = stmt.where(Registry.status_id != completed_status_id)
            result = await self.session.execute(stmt.limit(1))
            registry = result.scalar_one_or_none()

        if not registry:
            registry = await self.get_or_create_default_registry()

        # Проверка через status_id — безопасно и быстро
        if registry.status_id == completed_status_id:
            return {"status": "already_completed", "message": f"Регистр '{registry.shortname}' уже завершён.",
                    "registry_id": registry.id, "action_required": True}

        try:
            codes = await self.parse_and_save_codes(registry)
            return {"status": "success", "message": f"Успешно добавлено {len(codes)} ссылок.",
                    "registry_id": registry.id, "codes_added": len(codes)}
        except Exception as e:
            return {"status": "error", "message": f"Ошибка при парсинге: {str(e)}", "registry_id": registry.id}

    REQUIRED_STATUSES = {"new", "in progress", "completed"}

    @classmethod
    async def ensure_statuses_exist(cls, session: AsyncSession):
        """Проверяет и создаёт обязательные статусы, если их нет."""
        existing_statuses = await session.execute(select(Status.status))
        existing = {row[0] for row in existing_statuses.fetchall()}

        missing = cls.REQUIRED_STATUSES - existing
        if missing:
            for status_name in missing:
                new_status = Status(status=status_name)
                session.add(new_status)
            await session.commit()
