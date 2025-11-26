# app/support/parser/router.py
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.parser.model import Code, Name, Image, Rawdata, Status, Register
from app.support.parser import schemas


class RegisterRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=Register,
            prefix="/registers",
        )

    async def create(self, data: schemas.RegisterCreate,
                     session: AsyncSession = Depends(get_db)) -> schemas.RegisterCreateResponseSchema:
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
