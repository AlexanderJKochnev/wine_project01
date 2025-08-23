# app/core/models/base_model.py

"""
    Base Model for SqlAlchemy
    в случае изменения модели Base внести соответствующие изменения в app/core/schemas/base.py
"""
from datetime import datetime
from typing import Annotated
from sqlalchemy import func, text, Text, Integer
from sqlalchemy.orm import (DeclarativeBase, Mapped,
                            declared_attr, mapped_column)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import class_mapper
# from sqlalchemy.dialects.postgresql import MONEY
from sqlalchemy import DECIMAL
from decimal import Decimal

# annotation of some types of alchemy's fields

# primary key
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]

# datetime field with default value now()
created_at = Annotated[datetime, mapped_column(server_default=func.now())]

# datetime field with default and update value now()
updated_at = Annotated[datetime, mapped_column(server_default=func.now(),
                                               onupdate=datetime.now)]

# unique non-null string field
str_uniq = Annotated[str, mapped_column(unique=True,
                                        nullable=False, index=True)]

# non-unique nullable string field
str_null_true = Annotated[str, mapped_column(nullable=True)]
str_null_index = Annotated[str, mapped_column(nullable=True, index=True)]
str_null_false = Annotated[str, mapped_column(nullable=False)]

# int field with default value 0
nmbr = Annotated[int, mapped_column(server_default=text('0'))]

# text field wouthout default value
descr = Annotated[str, mapped_column(Text, nullable=True)]

# money
money = Annotated[Decimal, mapped_column(DECIMAL(10, 2), nullable=True)]

# volume, alcohol sugar percentage
volume = Annotated[Decimal, mapped_column(DECIMAL(4, 1), nullable=True)]

# int or none
ion = Annotated[int, mapped_column(nullable=True)]

# boolean triple
boolnone = Annotated[bool | None, mapped_column(nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    """ clear model with
        id only,
        common methods,
        table name
    """
    __abstarct__ = True

    id: Mapped[int_pk]
    # created_at: Mapped[created_at]
    # updated_at: Mapped[updated_at]
    # description: Mapped[descr]
    # description_ru: Mapped[descr]
    # name: Mapped[str_uniq]
    # name_ru: Mapped[str_null_index]

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """ Table name for postgresql is based on model name formatted
        as bellow
        """
        name = cls.__name__.lower()
        if name.endswith('model'):
            name = name[0:-5]
        if not name.endswith('s'):
            if name.endswith('y'):
                name = f'{name[0:-1]}ies'
            else:
                name = f'{name}s'
        return name

    def __str__(self):
        return self.name

    def __repr__(self):
        # return f"<Category(name={self.name})>"
        return str(self)

    def to_dict(self) -> dict:
        """Универсальный метод для конвертации объекта SQLAlchemy в словарь"""
        # Получаем маппер для текущей модели
        columns = class_mapper(self.__class__).columns
        # Возвращаем словарь всех колонок и их значений
        return {column.key: getattr(self, column.key) for column in columns}


class BaseAt:
    __abstract__ = True
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    # description: Mapped[descr]
    # description_ru: Mapped[descr]
    # name: Mapped[str_uniq]
    # name_ru: Mapped[str_null_index]


class BaseEn:
    __abstract__ = True
    name: Mapped[str_uniq]
    description: Mapped[descr]


class BaseLang:
    __abstract__ = True
    name_ru: Mapped[str_null_index]
    description_ru: Mapped[descr]


class BaseShort(BaseEn, BaseLang, Base):
    __abstract__ = True


class BaseFull(BaseShort, BaseAt):
    __abstract__ = True
