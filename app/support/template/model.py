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
     
    Все возможные варианты параметра cascade
    Основные опции:
    save-update - автоматически добавляет связанные объекты в сессию
    merge - распространяет операцию merge на связанные объекты
    expunge - распространяет операцию expunge на связанные объекты
    delete - удаляет связанные объекты при удалении родителя
    delete-orphan - удаляет объекты, которые были удалены из коллекции
    refresh-expire - распространяет refresh/expire на связанные объекты
    all - включает все опции кроме delete-orphan
"""

from __future__ import annotations   # ОБЯЗАТЕЛЬНО ДЛЯ FOREIGN RELATIONSHIPS
from sqlalchemy import ForeignKey
from sqlalchemy.orm import (relationship,
                            Mapped, mapped_column)
from typing import TYPE_CHECKING
from app.core.models.base_model import BaseFull

if TYPE_CHECKING:
    from app.support.country.model import Country


class Template(BaseFull):
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    country: Mapped["Country"] = relationship(back_populates="templates")

    drinks = relationship("Drink", back_populates="region")
