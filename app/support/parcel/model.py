# app.support.parcel.model.py
from __future__ import annotations

from html import escape
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from starlette.requests import Request

from app.core.config.project_config import settings
from app.core.models.base_model import plural, BaseFullFree, BaseFull
from app.service_registry import registers_search_update


if TYPE_CHECKING:
    from app.support.subregion.model import Subregion


@registers_search_update("drink.item")
class Parcel(BaseFull):
    """
        часть виноградника (верхняя, нижняя, возле леса - неуникальное имя)
    """
    lazy = settings.LAZY
    single_name = 'parcel'
    table_description = ("Отдельный, четко разграниченный участок виноградника, "
                         "который обладает своими уникальными природными характеристиками")
    plural_name = plural(single_name)
    cascade = settings.CASCADE
    # Обратная связь: many to one
    drinks = relationship(
        "Drink", back_populates=single_name, cascade=cascade, lazy=lazy
    )


@registers_search_update("drink.item")
class Site(BaseFullFree):
    """
    виноградник в subregion
    """
    table_description = "Официально признанный виноградник"
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'site'
    plural_name = plural(single_name)
    subregion_id: Mapped[int] = mapped_column(ForeignKey("subregions.id"), nullable=False, index=True)
    subregion: Mapped["Subregion"] = relationship(back_populates=plural_name, lazy=lazy)
    drinks = relationship("Drink", back_populates=single_name,
                          cascade=cascade,
                          lazy=lazy)

    __composite_fk_field__ = "subregion_id"
    """
    __table_args__ = (Index(
        "uq_  name_subregion_unique", "name", "subregion_id", unique=True, postgresql_nulls_not_distinct=True
        # Ключевой параметр
    ),)
    """

    @property
    def full_name(self) -> str:
        """
        Формирует полное имя: 'Имя_Сайта (Subregion, Region, Country)'
        """
        parts = []

        # Безопасно собираем географическую цепочку снизу вверх
        if self.subregion:
            parts.append(self.subregion.name)
            if self.subregion.region:
                parts.append(self.subregion.region.name)
                if self.subregion.region.country:
                    parts.append(self.subregion.region.country.name)

        geo_string = ", ".join([p for p in parts if p])

        if self.name and len(self.name.strip()) > 0:
            return f"{self.name} ({geo_string})" if geo_string else self.name

        return geo_string or "Без названия"

    def __admin_select2_repr__(self, request: Request) -> str:
        return f'<div>{escape(self.full_name)}</div>'
