# app/core/models/base_model.py

""" Base Model for SqlAlchemy """
from datetime import datetime
from typing import Annotated
from sqlalchemy import func, text, Text
from sqlalchemy.orm import (DeclarativeBase, Mapped,
                            declared_attr, mapped_column)
from sqlalchemy.ext.asyncio import AsyncAttrs

# annotation of some types of alchemy's fields

# primary key
int_pk = Annotated[int, mapped_column(primary_key=True)]

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

# int field with default value 0
nmbr = Annotated[int, mapped_column(server_default=text('0'))]

# text field wouthout default value
descr = Annotated[str, mapped_column(Text, nullable=True)]


class Base(AsyncAttrs, DeclarativeBase):
    """ Abstract class """
    __abstarct__ = True

    id: Mapped[int_pk]
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    description: Mapped[descr]
    description_ru: Mapped[descr]
    name: Mapped[str_uniq]
    name_ru: Mapped[str_null_index]

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
