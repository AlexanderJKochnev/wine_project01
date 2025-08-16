# app/support/template/model.py

"""
     - Наименование класса с большой буквы в ед. числе.
     - Стандартные поля по умолчанию заданы в базовом классе app.core.models.base_model.Base
     указывать их здесь не нужно (если только вдруг захотелось переопределить их).
     - Крайне осторожно относиться к заданию свойства поля - nullable=False без особой нужды его не использовать
     лучше писать nullable=True.
     - Для полей relationships внизу два примера:
        1. templates - соотношение один-ко-многим
        2. category - обратное соотношение много-к-одному
     - Если нужны другие поля - сначала поищи в аннотациях app.core.models.base_model, если нет тогда добавляй свое
     (но лучше добавить в аннотацию, а потом в модель - вдруг кому-то тоже пригодится.
     - По окончании редактировани удали все # noqa: ... и проверь на ошибки flake8, исправь.
     - удали эту инструкцию (только в этой папке. в app/support/template ничего не трогать
"""


from sqlalchemy import String, Text, text, ForeignKey   # noqa: F401
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)    # noqa: F401
from app.core.models.base_model import Base, str_null_true, str_null_index   # noqa: F401


class Template(Base):
    subtitle: Mapped[str_null_true]
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False)
    # Добавляем relationship
    category: Mapped["Category"] = relationship(back_populates="templates")  # noqa F821
