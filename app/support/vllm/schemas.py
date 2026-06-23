# app.support.vllm.schemas.py
from typing import Optional

from app.core.schemas.base import PkSchema, BaseModel
from app.support.drink.schemas import DrinkReadRelation
from app.support.ollama.schemas import PromptRead, ProptionRead, WriterRuleRead
from app.support.subcategory.schemas import SubcategoryReadRelation


class CreateSchema:
    drink_id: int
    lang_origin: str
    lang_result: str
    prompt_id: int
    writerrule_id: int
    proption_id: int
    result: str
    rate: Optional[int] = None
    duration: float


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

# ------ TmpTranslate -----


class TmpTranslateCreate(BaseModel):
    guid: int
    table: str
    field: str
    lang: str
    origin: str
    translate: str


class TmpTranslateUpdate(BaseModel):
    guid: Optional[int] = None
    table: Optional[str] = None
    field: Optional[str] = None
    lang: Optional[str] = None
    origin: Optional[str] = None
    translate: Optional[str] = None


class TmpTranslateRead(TmpTranslateUpdate):
    pass


class DrinkTranslateScoreCreate(BaseModel):
    guid: int
    origin: str
    destin: str
    prompt_id: int
    writerrule_id: int
    proption_id: int
    score: int


class DrinkTranslateScoreUpdate(BaseModel):
    guid: Optional[int] = None
    origin: Optional[str] = None
    destin: Optional[str] = None
    prompt_id: Optional[int] = None
    writerrule_id: Optional[int] = None
    proption_id: Optional[int] = None
    score: Optional[int] = None