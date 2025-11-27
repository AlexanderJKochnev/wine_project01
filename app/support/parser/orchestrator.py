# app/support/parser/orchestrator.py

import asyncio
import random
from sqlalchemy import select
# from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from app.support.parser.model import Registry, Code, Status, Name
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
                # --- новые поля ---
                name_link_tag="a",
                name_link_attr="href",
                name_link_parent_selector="div#cont_txt",
                pagination_selector=None,  # не используется напрямую
                pagination_link_tag="a",
                pagination_link_attr="href",

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

    async def _fetch_and_parse(self, url: str, timeout: int = 10) -> BeautifulSoup:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            # Кодировка windows-1251 указана в meta!
            html = resp.content.decode('windows-1251')
            return BeautifulSoup(html, 'html.parser')

    async def _extract_product_links(self, soup: BeautifulSoup, base_url: str, registry: Registry) -> List[
            tuple[str, str]]:
        container = soup.select_one(registry.name_link_parent_selector) if registry.name_link_parent_selector else soup
        if not container:
            return []

        links = []
        for tag in container.find_all(registry.name_link_tag or 'a'):
            href = tag.get(registry.name_link_attr or 'href')
            if not href:
                continue
            full_url = urljoin(base_url, href)
            # Фильтруем только ссылки с `-obj` (по шаблону из примера)
            if '-obj' not in full_url:
                continue
            name_text = (tag.get_text(strip=True) or "")[:255]
            links.append((full_url, name_text))
        return links

    async def _extract_pagination_urls(self, soup: BeautifulSoup, current_page_url: str, registry: Registry) -> List[
            str]:
        # Ищем <p>, содержащий "Выберите страницу"
        for p in soup.find_all('p'):
            if 'Выберите страницу' in p.get_text():
                pagination_block = p
                break
        else:
            return []

        urls = []
        for a in pagination_block.find_all(registry.pagination_link_tag or 'a'):
            href = a.get(registry.pagination_link_attr or 'href')
            if href:
                full = urljoin(current_page_url, href)
                if full not in urls:
                    urls.append(full)
        return urls

    async def parse_names_from_code(
            self, code: Code, registry: Registry, max_pages: Optional[int] = None
    ) -> dict:
        status_new = await StatusRepository.get_by_fields({"status": "new"}, Status, self.session)
        status_in_progress = await StatusRepository.get_by_fields({"status": "in progress"}, Status, self.session)
        status_completed = await StatusRepository.get_by_fields({"status": "completed"}, Status, self.session)

        # Начинаем с последнего сохранённого URL или с базового
        start_url = code.last_parsed_url or code.url
        to_visit = [start_url]
        # visited = set()
        visited: list = []
        total_saved = 0
        processed_pages = 0

        try:
            while to_visit and (max_pages is None or processed_pages < max_pages):
                current_url = to_visit.pop(0)
                if current_url in visited:
                    continue
                visited.add(current_url)

                # === 1. Загружаем и парсим страницу с retry ===
                try:
                    html = await self._fetch_with_retry(
                        current_url, timeout=registry.timeout or 10, max_retries=3, base_delay=1.0,
                        max_delay=10.0
                    )
                    soup = BeautifulSoup(html, 'html.parser')
                except Exception as e:
                    # Сохраняем прогресс ДО ошибки
                    code.status_id = status_in_progress.id
                    code.last_parsed_url = list(visited)[-1] if visited else code.url
                    await self.session.commit()
                    return {"status": "failed", "last_url": code.last_parsed_url, "saved": total_saved,
                            "error": f"Fetch failed on {current_url}: {str(e)}"}

                # === 2. Извлекаем ссылки на продукты ===
                product_links = self._extract_product_links_sync(soup, current_url, registry)
                for url, name in product_links:
                    # Проверяем уникальность по URL
                    existing = await self.session.execute(select(Name).where(Name.url == url))
                    if existing.scalar_one_or_none():
                        continue
                    try:
                        new_name = Name(
                            url=url, name=name[:255], code_id=code.id, status_id=status_new.id
                        )
                        self.session.add(new_name)
                        total_saved += 1
                    except Exception as e:
                        print(f"Skip duplicate or error on {url}: {e}")

                # === 3. Сохраняем прогресс: commit после каждой страницы ===
                code.status_id = status_in_progress.id
                code.last_parsed_url = current_url
                await self.session.commit()
                processed_pages += 1

                # === 4. Извлекаем пагинацию ===
                pagination_urls = self._extract_pagination_urls_sync(soup, current_url, registry)
                for url in pagination_urls:
                    if url not in visited and url not in to_visit:
                        to_visit.append(url)

            # === Завершение ===
            if max_pages is not None:
                # Обработали лимит — остаёмся в "in progress"
                code.status_id = status_in_progress.id
                code.last_parsed_url = list(visited)[-1] if visited else code.url
            else:
                # max_pages = None → обрабатываем всё
                if not to_visit:
                    # Больше страниц нет → завершаем
                    code.status_id = status_completed.id
                    code.last_parsed_url = None  # сброс прогресса
                else:
                    # Теоретически не должно быть, но на всякий
                    code.status_id = status_in_progress.id
                    code.last_parsed_url = list(visited)[-1] if visited else code.url

            await self.session.commit()

            return {"status": "completed" if (max_pages is None and not to_visit) else "partial", "saved": total_saved,
                    "pages_processed": processed_pages, "last_url": code.last_parsed_url, }

        except Exception as e:
            # Общая ошибка — сохраняем прогресс
            code.status_id = status_in_progress.id
            code.last_parsed_url = list(visited)[-1] if visited else code.url
            await self.session.commit()
            return {"status": "error", "last_url": code.last_parsed_url, "saved": total_saved, "error": str(e)}

    # --- Синхронные вспомогательные функции для run_in_executor ---

    def _extract_product_links_sync(self, soup, base_url, registry):
        container = soup.select_one(registry.name_link_parent_selector) if registry.name_link_parent_selector else soup
        if not container:
            return []
        links = []
        for tag in container.find_all(registry.name_link_tag or 'a'):
            href = tag.get(registry.name_link_attr or 'href')
            if not href:
                continue
            full_url = urljoin(base_url, href)
            if '-obj' not in full_url:
                continue
            name_text = (tag.get_text(strip=True) or "")[:255]
            links.append((full_url, name_text))
        return links

    def _extract_pagination_urls_sync(self, soup, current_page_url, registry):
        for p in soup.find_all('p'):
            if 'Выберите страницу' in p.get_text():
                pagination_block = p
                break
        else:
            return []
        urls = []
        for a in pagination_block.find_all(registry.pagination_link_tag or 'a'):
            href = a.get(registry.pagination_link_attr or 'href')
            if href:
                full = urljoin(current_page_url, href)
                if full not in urls:
                    urls.append(full)
        return urls

    async def _fetch_with_retry(
            self, url: str, timeout: int = 10, max_retries: int = 3, base_delay: float = 1.0,
            max_delay: float = 10.0, ) -> str:
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=httpx.Timeout(timeout)) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return resp.content.decode("windows-1251")
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as e:
                if attempt == max_retries:
                    raise e
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                await asyncio.sleep(delay)
        raise RuntimeError("Unreachable")
