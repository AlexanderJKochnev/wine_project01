# app/support/parser/service.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
from dateutil.relativedelta import relativedelta
from datetime import datetime, timezone
from app.core.services.service import Service
from app.support.parser import schemas
from app.support.parser import repository as repo
from app.support.parser import model as mode
from app.core.config.database.db_async import get_db


class RegistryService(Service):
    default = ['shortname', 'url']

    @classmethod
    async def create_relation(
            cls, data: schemas.RegistryCreateRelation,
            repository: repo.RegistryRepository,
            model: mode.Registry,
            session: AsyncSession
    ) -> schemas.RegistryRead:
        # pydantic model -> dict
        data_dict: dict = data.model_dump(exclude={'status'}, exclude_unset=True)
        if data.status:
            result, _ = await StatusService.get_or_create(data.status, repo.StatusRepository,
                                                          mode.Status, session)
            data_dict['status_id'] = result.id
        data_schema = schemas.RegistryCreate(**data_dict)
        result, _ = await cls.get_or_create(data_schema, repository, model, session)
        return result


class CodeService(Service):
    default = ['code', 'url']

    @classmethod
    async def create_relation(
            cls, data: schemas.CodeCreateRelation,
            repository: repo.CodeRepository,
            model: mode.Code,
            session: AsyncSession
    ) -> schemas.CodeRead:
        # pydantic model -> dict
        data_dict: dict = data.model_dump(exclude={'status'}, exclude_unset=True)
        if data.status:
            result, _ = await StatusService.get_or_create(data.status, repo.StatusRepository,
                                                          mode.Status, session)
            data_dict['status_id'] = result.id
        if data.registry:
            result = await RegistryService.create_relation(data.registry, repo.RegistryRepository,
                                                           mode.Registry, session)
            data_dict['registry_id'] = result.id

        data_schema = schemas.CodeCreate(**data_dict)
        result, _ = await cls.get_or_create(data_schema, repository, model, session)
        return result


class NameService(Service):
    @classmethod
    async def create_relation(
            cls, data: schemas.NameCreateRelation,
            repository: repo.NameRepository,
            model: mode.Name,
            session: AsyncSession
    ) -> schemas.NameRead:
        name_data: dict = data.model_dump(exclude={'status', 'code'}, exclude_unset=True)
        if data.status:
            result, _ = await StatusService.get_or_create(data.status, repo.StatusRepository,
                                                          mode.Status, session)
            name_data['status_id'] = result.id
        if data.code:
            result = await CodeService.create_relation(data.code, repo.CodeRepository,
                                                       mode.Code, session)
            name_data['code_id'] = result.id
        name = schemas.NameCreate(**name_data)
        result, _ = await cls.get_or_create(name, repository, model, session)
        return result


class ImageService(Service):
    default = ['image_id', 'name_id']

    @classmethod
    async def create_relation(
            cls, data: schemas.ImageCreateRelation,
            repository: repo.ImageRepository,
            model: mode.Image,
            session: AsyncSession
    ) -> schemas.NameRead:
        image_data: dict = data.model_dump(exclude={'name'}, exclude_unset=True)
        if data.name:
            result = await NameService.create_relation(data.name, repo.NameRepository,
                                                       mode.Name, session)
            image_data['name_id'] = result.id
        image = schemas.ImageCreate(**image_data)
        result, _ = await cls.get_or_create(image, repository, model, session)
        return result


class RawdataService(Service):
    default = ['name_id']

    @classmethod
    async def create_relation(
            cls, data: schemas.RawdataCreateRelation,
            repository: repo.RawdataRepository,
            model: mode.Rawdata,
            session: AsyncSession
    ) -> schemas.RawdataRead:
        raw_data: dict = data.model_dump(exclude={'name', 'status'}, exclude_unset=True)
        if data.status:
            result, _ = await StatusService.get_or_create(data.status, repo.StatusRepository,
                                                          mode.Status, session)
            raw_data['status_id'] = result.id
        if data.name:
            result = await NameService.create_relation(data.name, repo.NameRepository,
                                                       mode.Name, session)
            raw_data['name_id'] = result.id
        rawdata = schemas.RawdataCreate(**raw_data)
        result, _ = await cls.get_or_create(rawdata, repository, model, session)

        return result


class StatusService(Service):
    default = ['status']


class TaskLogService:
    model = mode.TaskLog

    @classmethod
    async def add(cls, task_name: str, job_id: str,
                  name_id: int, session: AsyncSession = Depends(get_db)) -> int:
        task_log = cls.model(task_name=task_name,
                             task_id=job_id, status="started", entity_id=name_id,
                             started_at=datetime.now(timezone.utc))
        session.add(task_log)
        await session.commit()
        return task_log.id

    @classmethod
    async def add_with_session(cls, task_name: str, job_id: str,
                               name_id: int, session: AsyncSession) -> int:
        task_log = cls.model(task_name=task_name,
                             task_id=job_id, status="started", entity_id=name_id,
                             started_at=datetime.now(timezone.utc))
        session.add(task_log)
        # Don't commit here - let the caller handle it
        return task_log.id

    @classmethod
    async def update(cls, task_log_id: str, task_log_status: str,
                     task_log_error: str, session: AsyncSession = Depends(get_db)):
        task_log = await session.get(cls.model, task_log_id)
        if task_log:
            task_log.status = task_log_status
            task_log.error = task_log_error
            task_log.finished_at = datetime.now(timezone.utc)
            await session.commit()
        return True

    @classmethod
    async def update_with_session(cls, task_log_id: int, task_log_status: str,
                                  task_log_error: str, session: AsyncSession):
        task_log = await session.get(cls.model, task_log_id)
        if task_log:
            task_log.status = task_log_status
            task_log.error = task_log_error
            task_log.finished_at = datetime.now(timezone.utc)
            # Don't commit here - let the caller handle it
        return True

    @classmethod
    async def clear(cls, session: AsyncSession = Depends(get_db)):
        cutoff_date = (datetime.now(timezone.utc) - relativedelta(days=2)).isoformat()
        stmt = delete(cls.model).where((cls.model.created_at < cutoff_date) &
                                       (cls.model.status == 'success'))
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount
