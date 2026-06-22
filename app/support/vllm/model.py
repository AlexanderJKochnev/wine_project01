# app/support/subcategory/model.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config.project_config import settings
from app.core.models.base_model import Base, BaseAt, int_null_index, plural, str_null_false

if TYPE_CHECKING:
    from app.support.drink.model import Drink
    from app.support.ollama.model import Prompt, WriterRule, Proption


class TranslateRawData(Base, BaseAt):
    lazy = settings.LAZY
    cascade = settings.CASCADE
    single_name = 'translaterawdata'
    plural_name = plural(single_name)
    # источник drink
    drink_id: Mapped[int] = mapped_column(ForeignKey("drinks.id"), nullable=False, index=True)
    drink: Mapped["Drink"] = relationship(cascade=cascade, lazy=lazy)
    # язык оригинала - суффикс поля
    lang_origin: Mapped[str_null_false]
    lang_result: Mapped[str_null_false]
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id"), nullable=False, index=True)
    prompt: Mapped["Prompt"] = relationship(cascade=cascade, lazy=lazy)
    writerrule_id: Mapped[int] = mapped_column(ForeignKey("writerrules.id"), nullable=False, index=True)
    writerrule: Mapped["WriterRule"] = relationship(cascade=cascade, lazy=lazy)
    proption_id: Mapped[int] = mapped_column(ForeignKey("proptions.id"), nullable=False, index=True)
    proption: Mapped["Proption"] = relationship(cascade=cascade, lazy=lazy)
    # subcategory_id: Mapped[int] = mapped_column(ForeignKey("subcategories.id"), nullable=False, index=True)
    # subcategory: Mapped["Subcategory"] = relationship(cascade=cascade, lazy=lazy)
    # isolanguage_id: Mapped[int] = mapped_column(ForeignKey("isolanguages.id"), nullable = False, index = True)
    # isolanguage: Mapped["ISOLanguage"] = relationship(back_populates = plural_name, cascade = cascade, lazy = lazy)
    result: Mapped[str] = mapped_column(Text)
    rate: Mapped[int_null_index]  # оценка перевода
    duration: Mapped[float] = mapped_column(Float, nullable=False)

    def __str__(self):
        # переоопределять в особенных формах
        # or "" на всякий случай если обязательное поле вдруг окажется необязательным и пустым
        return str(self.name) or ""

    __table_args__ = (UniqueConstraint(
        'drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id',
        name='uq_translate_raw_data_unique_combo'
    ),)


class TmpTranslate(Base):
    """
        модель для временного хранения переводов
    """
    __tablename__ = 'tmptranslates'
    # id переводимой записи
    guid: Mapped[int] = mapped_column(Integer, index=True, nullable=False, unique=False)
    # имя таблицы
    table: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=False)
    # имя переводимого поля (уже с префиксом)
    field: Mapped[str] = mapped_column(String, index=True, nullable=False, unique=False)
    # lang: Mapped[str] = mapped_column(String(2), index=True, nullable=False, unique=False)
    origin: Mapped[str] = mapped_column(Text, nullable=False, unique=False)
    translate: Mapped[str] = mapped_column(Text, nullable=False, unique=False)

    __table_args__ = (UniqueConstraint('id', 'table', 'field', 'lang',
                                       name='uq_tmp_translate_id_table_field_lang'),)
