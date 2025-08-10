# app/support/template/models.py

""" SQLAlchemy models """
from sqlalchemy import String, Text, text   # noqa: F401
from sqlalchemy.orm import (relationship,   # noqa: F401
                            Mapped, mapped_column)    # noqa: F401
from sqlalchemy import ForeignKey   # noqa: F401
from app.core.models.base_model import Base, nmbr

"""
     - Наименование класса с большой буквы в ед. числе.
     - Стандартные поля по умолчанию заданы в базовом классе app.core.models.base_model.Base
     указывать их здесь не нужно (если только вдруг захотелось переопределить их).
     - Крайне осторожно относиться к заданию свойства поля - nullable=False без особой нужды его не использовать
     лучше писать nullable=True.
     - Для полей relationships внизу два примера:
        1. drinks - соотношение один-ко-многим
        2. category - обратное соотношение много-к-одному
     - Если нужны другие поля - сначала поищи в аннотациях app.core.models.base_model, если нет тогда добавляй свое
     (но лучше добавить в аннотацию, а потом в модель - вдруг кому-то тоже пригодится.
     - По окончании редактировани удали все # noqa: ... и проверь на ошибки flake8, исправь.
     
     - за образец лучше взять данные из app.support.drink
"""


class Template(Base):
    count_drink: Mapped[nmbr] = mapped_column(server_default=text('0'))
    # Обратная связь: один ко многим
    # --------one-to-many-----------------------------------------
    drinks = relationship("Drink",
                          back_populates="category",
                          cascade="all, delete-orphan")
    # -------many-to-one------------------------------------------
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False)
    # Добавляем relationship
    category: Mapped["Category"] = (relationship(back_populates="drinks"))  # noqa: F821
