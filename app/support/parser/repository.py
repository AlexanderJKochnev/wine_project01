# app/support/parser/repository.py
from typing import List, Optional
from sqlalchemy.dialects import postgresql
from sqlalchemy import func, select
from sqlalchemy.sql.functions import count
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.routers.base import delta
from app.core.repositories.sqlalchemy_repository import ModelType, Repository
from app.support.parser.model import Code, Image, Name, Rawdata, Registry, Status
from app.core.utils.common_utils import search_local


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

    @classmethod
    async def search_fts(cls, search_str: str, model: ModelType, session: AsyncSession,
                         skip: int = None, limit: int = None) -> Optional[List[ModelType]]:
        """
             полнотекстовый поиск с постарничным выводом
        """
        if search_str is None or search_str.strip() == '':
            # Если search_str пустой, возвращаем все записи с пагинацией
            return await cls.get_all(delta, skip, limit, model, session)
        # определяем язык запроса
        lang = search_local(search_str)
        # строим поискковую строку
        match lang:
            case 1:
                language = 'russian'
                fts_column = Rawdata.fts_russian
            case 2:
                language = 'english'
                fts_column = Rawdata.fts_english
            case _:
                language = 'english'
                fts_column = Rawdata.fts_english
        ts_query = func.to_tsquery(language, search_str)
        search_condition = fts_column.op('@@')(ts_query)
        stmt = select(Rawdata).where(search_condition).order_by(Rawdata.id)
        stmt = stmt.offset(skip).limit(limit)

        # ----- отладка -------
        compiled_sql = stmt.compile(dialect=postgresql)
        print("--- Сгенерированный SQL (без параметров) ---")
        print(compiled_sql)
        print("\n--- Сгенерированный SQL (с подставленными параметрами) ---")
        print(compiled_sql.string)
        #  ----- end -----
        count_stmt = select(count(Rawdata.id)).where(search_condition)
        total_count = session.execute(count_stmt).scalar() or 0
        if total_count == 0:
            return [], 0
        result = session.execute(stmt).scalars().all()
        return result, total_count


class StatusRepository(Repository):
    model = Status
