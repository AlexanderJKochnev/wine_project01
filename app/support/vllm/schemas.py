# app.support.vllm.schemas.py
from typing import Optional

from pydantic import Field, field_validator

from app.core.schemas.base import PkSchema, BaseModel
from app.support.drink.schemas import DrinkReadRelation
from app.support.ollama.schemas import PromptRead, ProptionRead, WriterRuleRead
from app.support.subcategory.schemas import SubcategoryReadRelation


class CreateSchema:
    drink_id: int
    lang_origin: str
    lang_result: str
    prompt_id: id
    writerrule_id: id
    proption_id: id
    proption: id
    subcategory_id: id
    result: str
    rate: int
    duration: float = Field(..., ge=0.5, description="Продолжительность в секундах (шаг 0.5)")

    @field_validator("duration")
    @classmethod
    def round_to_half_second(cls, v: float) -> float:
        # Умножаем на 2, округляем до целого, делим на 2
        # Например: 1.23 -> 2.46 -> 2.0 -> 1.0
        # Например: 1.45 -> 2.90 -> 3.0 -> 1.5
        return round(v * 2) / 2.0


class UpdateSchema:
    drink_id: Optional[int] = None
    lang_origin: Optional[str] = None
    lang_result: Optional[str] = None
    prompt_id: Optional[int] = None
    writerrule_id: Optional[int] = None
    proption_id: Optional[int] = None
    proption: Optional[int] = None
    subcategory_id: Optional[int] = None
    result: Optional[str] = None
    rate: Optional[int] = None


class RelationSchema:
    drink: Optional[DrinkReadRelation] = None
    lang_origin: Optional[str] = None
    lang_result: Optional[str] = None
    prompt: Optional[PromptRead] = None
    writerrule: Optional[WriterRuleRead] = None
    proption: Optional[ProptionRead] = None
    subcategory: Optional[SubcategoryReadRelation] = None
    result: Optional[str] = None
    rate: Optional[int] = None


class TranslateRawDataCreate(CreateSchema, BaseModel):
    pass


class TranslateRawDataUpdate(UpdateSchema, BaseModel):
    pass


class TranslateRawDataRead(UpdateSchema, PkSchema):
    duration: Optional[float] = None


class TranslateRawDataReadRelation(RelationSchema, PkSchema):
    duration: Optional[float] = None
