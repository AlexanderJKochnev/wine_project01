# app/support/parser/router.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends, Query
from typing import Optional
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter, LightRouter
from app.support.parser.model import Code, Name, Image, Rawdata, Status, Registry
from app.support.parser import schemas
from app.support.parser.orchestrator import ParserOrchestrator
from app.support.parser.repository import StatusRepository


class OrchestratorRouter(LightRouter):
    def __init__(self):
        super().__init__(prefix='/parser')

    def setup_routes(self):
        self.router.add_api_route(
            "", self.endpoints, methods=["POST"])  # , response_model=self.create_schema)
        self.router.add_api_route("/name", self.parse_names_endpoint, methods=["POST"])

    async def endpoints(self, shortname: str = None, url: str = None,
                        session: AsyncSession = Depends(get_db)):
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

    async def create_relation(self, data: schemas.CodeCreateRelation,
                              session: AsyncSession = Depends(get_db)) -> schemas.CodeRead:
        result = await super().create_relation(data, session)
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
