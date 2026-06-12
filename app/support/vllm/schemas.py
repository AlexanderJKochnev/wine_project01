# app.support.vllm.schemas.py
from typing import Optional

from pydantic import BaseModel, Field

from app.core.enum import Preset, Writers


class PromptsModel(BaseModel):
    phrase: Optional[str] = Field(..., description="текст для перевода")
    prompt: Optional[str] = Field(..., description="системный prompt. Должен содержать ключевое слово {lang}")
    proption: Preset = Field(None, description="Типовые настройки качество/скорость")
    writer: Writers = Field(None, description="Типовые правила перевода")
    langs: Optional[str] = Field(
        'ru, en', description="Язык (языки) перевода двух-значные коды через "
        "запятую, например 'ru, fr, zh'"
    )
