# app/support/parser/repository.py
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.support.parser.model import Code, Name, Image, Rawdata, Status


class CodeRepository(Repository):
    model = Code

    @classmethod
    def get_query(cls, model: ModelType):
        return select(model).options(selectinload(Status.status))


class NameRepository(Repository):
    model = Name

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(model).options(selectinload(model.code),
                                     selectinload(Status.status))


class ImageRepository(Repository):
    model = Image

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(model).options(selectinload(model.name))


class RawdataRepository(Repository):
    model = Rawdata

    @classmethod
    def get_query(cls, model: ModelType):
        # Добавляем загрузку связи с relationships
        return select(model).options(selectinload(model.name),
                                     selectinload(Status.status))


class StatusRepository(Repository):
    model = Status
