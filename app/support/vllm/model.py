# app/support/subcategory/model.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config.project_config import settings
from app.core.models.base_model import Base, BaseAt, int_null_index, plural, str_null_false

if TYPE_CHECKING:
    from app.support.drink.model import Drink
    from app.support.ollama.model import ISOLanguage, Prompt, WriterRule, Proption
    from app.support.subcategory.model import Subcategory


class TranslateRawData(Base, BaseAt):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'translaterawdata'
    plural_name = plural(single_name)
    # источник drink
    drink_id: Mapped[int] = mapped_column(ForeignKey("drinks.id"), nullable=False, index=True)
    drink: Mapped["Drink"] = relationship(back_populates=plural_name, cascade=cascade, lazy=lazy)
    # язык оригинала - суффикс поля
    lang_origin: Mapped[str_null_false]
    lang_result: Mapped[str_null_false]
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id"), nullable=False, index=True)
    prompt: Mapped["Prompt"] = relationship(back_populates=plural_name, cascade=cascade, lazy=lazy)
    writerrule_id: Mapped[int] = mapped_column(ForeignKey("writerrules.id"), nullable=False, index=True)
    writerrule: Mapped["WriterRule"] = relationship(back_populates=plural_name, cascade=cascade, lazy=lazy)
    proption_id: Mapped[int] = mapped_column(ForeignKey("proptions.id"), nullable=False, index=True)
    proption: Mapped["Proption"] = relationship(back_populates=plural_name, cascade=cascade, lazy=lazy)
    subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"), nullable=False, index=True)
    subcategory: Mapped["Subcategory"] = relationship(back_populates=plural_name, cascade=cascade, lazy=lazy)
    isolanguage_id: Mapped[int] = mapped_column(ForeignKey("isolanguages.id"), nullable = False, index = True)
    isolanguage: Mapped["ISOLanguage"] = relationship(back_populates = plural_name, cascade = cascade, lazy = lazy)
    result: Mapped[str] = mapped_column(Text)
    rate: Mapped[int_null_index]  # оценка перевода

    def __str__(self):
        # переоопределять в особенных формах
        # or "" на всякий случай если обязательное поле вдруг окажется необязательным и пустым
        return str(self.name) or ""

    __table_args__ = (UniqueConstraint(
        'drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id', 'isolanguage_id',
        'subcategory_id',
        name='uq_translate_raw_data_unique_combo'
    ),)
