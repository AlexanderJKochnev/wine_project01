# app/support/subcategory/model.py
from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette.requests import Request

from app.core.config.project_config import settings
from app.core.models.base_model import BaseFullFree, plural, ColorMixin
from app.service_registry import registers_search_update

if TYPE_CHECKING:
    from app.support.category.model import Category


@registers_search_update("drink.item")
class Subcategory(ColorMixin, BaseFullFree):
    lazy = settings.LAZY
    table_description = "Категории и виды алкогольных и безалкогольных напитков"
    cascade = settings.CASCADE
    single_name = 'subcategory'
    plural_name = plural(single_name)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    category: Mapped["Category"] = relationship(back_populates=plural_name, lazy=lazy)
    drinks = relationship("Drink", back_populates=single_name,
                          cascade=cascade,
                          lazy=lazy)
    # name: Mapped[str_null_true]
    # __table_args__ = (UniqueConstraint('name', 'category_id', name='uq_subcategory_name_category'),)
    __composite_fk_field__ = "category_id"

    @property
    def full_name(self) -> str:
        """Полное имя с категорией"""
        return f"{self.name} ({self.category.name if self.name else self.category.name})"

    def __str__(self) -> str:
        """Строковое представление с включением данных из связанной модели"""
        # Вариант 1: Если категория точно загружена
        # return f"{self.name} ({self.category.name})"
        return self.full_name

    def __admin_select2_repr__(self, request: Request) -> str:
        return f'<div>{escape(self.full_name)}</div>'
