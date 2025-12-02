# app/support/parser/router.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from fastapi import Depends, Query
from typing import Optional
from arq import create_pool
from app.worker import redis_settings
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter, LightRouter
from app.support.parser.model import Code, Name, Image, Rawdata, Status, Registry, TaskLog
from app.support.parser import schemas
from app.support.parser.orchestrator import ParserOrchestrator
from app.support.parser.repository import StatusRepository

background_tasks = set()  # чтобы ссылка не удалилась


class OrchestratorRouter(LightRouter):
    def __init__(self):
        super().__init__(prefix='/parser')

    def setup_routes(self):
        self.router.add_api_route(
            "", self.endpoints, methods=["POST"])  # , response_model=self.create_schema)
        self.router.add_api_route("/name", self.parse_names_endpoint, methods=["POST"])
        self.router.add_api_route("/raw", self.parse_raw_endpoint, methods=["POST"])
        self.router.add_api_route("/raw/backgound", self.start_background_parsing, methods=["POST"])
        self.router.add_api_route("/raw/enqueue", self.enqueue_raw_parsing, methods=['POST'])
        self.router.add_api_route("/raw/enqueue-all", self.enqueue_all_raw_parsing, methods=['POST'])
        self.router.add_api_route("/logs", self.get_task_logs, methods=['GET'])
        self.router.add_api_route("/task/cancel", self.cancel_task, methods=['POST'])

    async def endpoints(self, shortname: str = None, url: str = None,
                        session: AsyncSession = Depends(get_db)):
        """
            получение кодов ФРАП
        """
        orchestrator = ParserOrchestrator(session)
        result = await orchestrator.run(shortname=shortname, url=url)
        if result["status"] == "alreadycompleted":
            # Тут можно вернуть 409 Conflict или предложить "force"
            return {"detail": result["message"], "action": "Повторить обработку? Используйте ?force=true"}
        return result

    async def parse_names_endpoint(
        self,
        max_pages: Optional[int] = Query(None,
                                         description="Макс. кол-во страниц для обработки (для тестов)"),
        code_id: Optional[int] = None, session: AsyncSession = Depends(get_db)
    ):
        """
            получение наименований продукции зарегистрированной в ФРАП
        """
        # Если code_id не задан — берем первую запись со статусом != 'completed'
        if code_id is None:
            status_completed = await StatusRepository.get_by_fields({"status": "completed"}, Status, session)
            stmt = select(Code)
            if status_completed:
                stmt = stmt.where(Code.status_id != status_completed.id)
            stmt = stmt.order_by(Code.id).limit(1)
            result = await session.execute(stmt)
            code = result.scalar_one_or_none()
            if not code:
                return {"error": "Нет необработанных записей в Code"}
        else:
            code = await session.get(Code, code_id)
            if not code:
                return {"error": "Code not found"}

        registry = await session.get(Registry, code.registry_id)
        if not registry:
            return {"error": "Registry not found"}

        orchestrator = ParserOrchestrator(session)
        result = await orchestrator.parse_names_from_code(code, registry, max_pages=max_pages)

        return {"code_id": code.id, "result": result}

    async def parse_raw_endpoint(self,
                                 name_id: Optional[int] = Query(
                                     None, description="ID записи Name. "
                                                       "Если не указан — обрабатывается первая "
                                                       "незавершённая."
                                 ), session: AsyncSession = Depends(get_db)
                                 ):
        """
        получение инфорации о продукции по id (не используется)
        """
        if name_id is not None:
            name = await session.get(Name, name_id)
            if not name:
                return {"error": "Name not found"}
        else:
            # Берём первую запись Name со статусом != completed
            status_completed = await StatusRepository.get_by_fields(
                {"status": "completed"}, Status, session
            )
            stmt = select(Name)
            if status_completed:
                stmt = stmt.where(Name.status_id != status_completed.id)
            stmt = stmt.order_by(Name.id).limit(1)
            result = await session.execute(stmt)
            name = result.scalar_one_or_none()
            if not name:
                return {"error": "No unprocessed Name records found"}

        orchestrator = ParserOrchestrator(session)
        result = await orchestrator.parse_rawdata_from_name(name)
        return result

    async def start_background_parsing(self, session: AsyncSession = Depends(get_db)):

        orchestrator = ParserOrchestrator(session)
        """
            Это не production-ready для долгих задач (при рестарте приложения задача прервётся).
            Для продакшена — использовать Celery + Redis/RabbitMQ или arq.
        """
        async def run():
            result = await orchestrator.process_all_names_in_background()
            print("Background parsing finished:", result)

        task = asyncio.create_task(run())
        background_tasks.add(task)
        task.add_done_callback(background_tasks.discard)

        return {"message": "Background parsing started"}

    async def enqueue_raw_parsing(self, name_id: int):
        redis = await create_pool(redis_settings())
        job = await redis.enqueue_job('parse_rawdata_task', name_id)
        return {"job_id": job.job_id}

    async def enqueue_all_raw_parsing(self):
        from sqlalchemy import select
        from app.support.parser.model import Name, Status
        from app.core.config.database.db_async import AsyncSessionLocal

        redis = await create_pool(redis_settings())
        """
        парсинг данных ФРАП
        """
        async with AsyncSessionLocal() as session:
            status_completed = await session.execute(select(Status).where(Status.status == "completed"))
            status_completed = status_completed.scalar_one_or_none()
            query = select(Name.id)
            if status_completed:
                query = query.where(Name.status_id != status_completed.id)
            names = await session.execute(query)
            for (name_id,) in names:
                await redis.enqueue_job('parse_rawdata_task', name_id)
        return {"message": "All raw parsing jobs enqueued"}

    async def get_task_logs(self,
                            status: str = None, skip: int = 0, limit: int = 100, session: AsyncSession = Depends(get_db)
                            ):
        """
        Просмотр arq логов (выполнение фоновых задач: старт, завершение, критические ошибки
        """
        stmt = select(TaskLog).order_by(TaskLog.started_at.desc()).offset(skip).limit(limit)
        if status:
            stmt = stmt.where(TaskLog.status == status)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def cancel_task(self,
                          task_id: str, session: AsyncSession = Depends(get_db)
                          ):
        """
            отмена выполенния фоновых задач
        """
        stmt = select(TaskLog).where(TaskLog.task_id == task_id)
        result = await session.execute(stmt)
        task_log = result.scalar_one_or_none()
        if not task_log:
            return {"error": "Task not found"}

        if task_log.status in ("success", "failed", "cancelled"):
            return {"error": "Task already finished"}

        task_log.cancel_requested = True
        await session.commit()
        return {"status": "cancel requested", "task_id": task_id}


class RegistryRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Registry,
            prefix="/registry",
        )

    async def create(self, data: schemas.RegistryCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.RegistryCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: schemas.CodeUpdate,
                    session: AsyncSession = Depends(get_db)) -> schemas.CodeCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: schemas.RegistryCreateRelation,
                              session: AsyncSession = Depends(get_db)):  # -> schemas.RegistryCreateResponseSchema:
        # result = await super().create_relation(data, session)
        result = await self.create(data, session)
        return result


class CodeRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Code,
            prefix="/codes",
        )

    async def create(self, data: schemas.CodeCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.CodeCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: schemas.CodeUpdate,
                    session: AsyncSession = Depends(get_db)) -> schemas.CodeCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: schemas.CodeCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> schemas.CodeRead:
        result = await super().create_relation(data, session)
        return result


class StatusRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Status,
            prefix="/status",
        )

    async def create(self, data: schemas.StatusCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.StatusCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: schemas.StatusUpdate,
                    session: AsyncSession = Depends(get_db)) -> schemas.StatusCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: schemas.StatusCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> schemas.StatusRead:
        result = await super().create_relation(data, session)
        return result


class NameRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Name,
            prefix="/names",
        )

    async def create(self, data: schemas.NameCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.NameCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: schemas.NameUpdate,
                    session: AsyncSession = Depends(get_db)) -> schemas.NameCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: schemas.NameCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> schemas.NameRead:
        result = await super().create_relation(data, session)
        return result


class RawdataRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Rawdata,
            prefix="/rawdatas",
        )

    async def create(self, data: schemas.RawdataCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.RawdataCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: schemas.RawdataUpdate,
                    session: AsyncSession = Depends(get_db)) -> schemas.RawdataCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: schemas.RawdataCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> schemas.RawdataRead:
        result = await super().create_relation(data, session)
        print('=================', result)
        return result


class ImageRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Image,
            prefix="/images",
        )

    async def create(self, data: schemas.ImageCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.ImageCreateResponseSchema:
        return await super().create(data, session)

    async def patch(self, id: int,
                    data: schemas.ImageUpdate,
                    session: AsyncSession = Depends(get_db)) -> schemas.ImageCreateResponseSchema:
        return await super().patch(id, data, session)

    async def create_relation(self, data: schemas.ImageCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> schemas.ImageRead:
        result = await super().create_relation(data, session)
        return result
