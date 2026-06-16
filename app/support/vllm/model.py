# app/support/subcategory/model.py
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, SmallInteger, Text, UniqueConstraint
from sqlalchemy.ext.hybrid import hybrid_property
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
    _duration_half_secs: Mapped[int] = mapped_column(
        "duration_half_secs", SmallInteger, nullable=False
    )

    # Гибридное свойство для удобной работы в Python (в секундах)
    @hybrid_property
    def duration(self) -> float:
        return self._duration_half_secs / 2.0

    @duration.setter
    def duration(self, value: float) -> None:
        # Округляем до ближайших 0.5 секунды и переводим в целое
        self._duration_half_secs = int(round(value * 2))

    def __str__(self):
        # переоопределять в особенных формах
        # or "" на всякий случай если обязательное поле вдруг окажется необязательным и пустым
        return str(self.name) or ""

    __table_args__ = (UniqueConstraint(
        'drink_id', 'lang_origin', 'prompt_id', 'writerrule_id', 'proption_id',
        name='uq_translate_raw_data_unique_combo'
    ),)
