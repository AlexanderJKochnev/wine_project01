# app/support/parser/service.py
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.services.service import Service
from app.support.parser import schemas
from app.support.parser import repository as repo
from app.support.parser import model as mode


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
        image = schemas.ImageRead(**image_data)
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
        rawdata = schemas.RawdataRead(**raw_data)
        result, _ = await cls.get_or_create(rawdata, repository, model, session)

        return result


class StatusService(Service):
    default = ['status']
