# app.core.schemas.translate_schema.py
from typing import List

from pydantic import BaseModel, Field


class GenerationParams(BaseModel):
    """Параметры генерации vLLM"""
    temperature: float = Field(
        default=0.1, ge=0.0, le=2.0, description="Температура генерации. 0.0 = детерминированный режим"
    )
    top_p: float = Field(
        default=0.85, ge=0.0, le=1.0,
        description="Nucleus sampling. Ограничивает выбор токенов кумулятивной вероятностью"
    )
    top_k: int = Field(
        default=50, ge=0, le=200, description="Ограничение выборки K наиболее вероятных токенов. 0 = отключен"
    )
    frequency_penalty: float = Field(
        default=0.2, ge=-2.0, le=2.0, description="Штраф за повторение токенов (учитывает частоту)"
    )
    presence_penalty: float = Field(
        default=0.1, ge=-2.0, le=2.0, description="Штраф за повторение тем (бинарный)"
    )
    repeat_penalty: float = Field(
        default=1.1, ge=0.5, le=2.0, description="Экспоненциальный штраф за повторение токенов"
    )
    max_tokens: int = Field(
        default=2048, ge=1, le=4096, description="Максимальное количество токенов в ответе"
    )
    seed: int = Field(
        default=42, ge=0, le=2147483647, description="Сид для воспроизводимости"
    )
    min_p: float = Field(
        default=0.04, ge=0.0, le=1.0, description="Минимальная вероятность токена относительно max_probability"
    )
    typical_p: float = Field(
        default=0.92, ge=0.0, le=1.0, description="Typical sampling. Отбрасывает нетипичные токены"
    )
    stop: List[str] = Field(default=[], description="Стоп-последовательности")

    class Config:
        json_schema_extra = {"example": {"temperature": 0.1, "top_p": 0.85, "top_k": 50, "frequency_penalty": 0.2,
                                         "presence_penalty": 0.1, "repeat_penalty": 1.1, "max_tokens": 2048, "seed": 42, "min_p": 0.04,
                                         "typical_p": 0.92, "stop": []}}
