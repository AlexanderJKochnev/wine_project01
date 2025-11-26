# app/support/parser/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.support.parser.model import Code, Name, Image, Rawdata, Status, Registry


class RegistryRepository(Repository):
    model = Registry

    @classmethod
    def get_query(cls, model: ModelType):
        return select(model).options(selectinload(model.status))


class CodeRepository(Repository):
    model = Code

    @classmethod
    def get_query(cls, model: ModelType):
        return select(model).options(selectinload(model.registry)
                                     .selectinload(Registry.status),
                                     selectinload(model.status))


class NameRepository(Repository):
    model = Name

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(model).options(selectinload(model.code)
                                     .selectinload(Code.status),
                                     selectinload(model.status))


class ImageRepository(Repository):
    model = Image

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(model).options(selectinload(model.name)
                                     .options(selectinload(Name.status),
                                              selectinload(Name.code)
                                              .selectinload(Code.status)))


class RawdataRepository(Repository):
    model = Rawdata

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(model).options(selectinload(Rawdata.name)
                                     .options(selectinload(Name.status),
                                              selectinload(Name.code)
                                              .selectinload(Code.status)),
                                     selectinload(Rawdata.status))  # Свой статус


class StatusRepository(Repository):
    model = Status
