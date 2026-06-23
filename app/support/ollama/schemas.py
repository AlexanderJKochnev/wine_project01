# app.suport.ollama.schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import model_validator, Field, field_validator, computed_field
from app.core.schemas.base import PkSchema, BaseModel
from app.support import CategoryRead


# from app.support.ollama.model import Prompt


class Subcategories:
    # subcategory_ids: Optional[List[int]] = None
    pass


class CustomCreate:
    category_id: int
    active: bool = True


class CustomRead:
    category: CategoryRead
    active: Optional[bool] = None


class CustomUpdate:
    category_id: Optional[int] = None
    active: Optional[bool] = None


class WriterRuleCreate(Subcategories, BaseModel, CustomCreate):
    name: str
    prompt: str


class WriterRuleRead(Subcategories, BaseModel, CustomRead):
    id: int
    name: Optional[str] = None
    prompt: Optional[str] = None


class WriterRuleUpdate(Subcategories, BaseModel, CustomUpdate):
    name: Optional[str] = None
    prompt: Optional[str] = None


class ProptionCustom(BaseModel):
    # system_prompt: Optional[str] = Field(None, description="Инструкция для модели")
    num_ctx: Optional[int] = Field(4096, ge=1, le=131072)
    temperature: Optional[float] = Field(0.1, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(0.1, ge=0.0, le=1.0)
    top_k: Optional[int] = Field(40, ge=0)
    seed: Optional[int] = None
    num_predict: Optional[int] = Field(1000, ge=-1)
    repeat_penalty: Optional[float] = Field(1.1, ge=0.0, le=2.0)
    stop: Optional[List[str]] = None

    # Новые поля:
    min_p: Optional[float] = Field(
        0.05, ge=0.0, le=1.0, description="Минимальная вероятность относительно лидера"
    )
    typical_p: Optional[float] = Field(0.9, ge=0.0, le=1.0, description="Типичная вероятность (Typical sampling)")
    frequency_penalty: Optional[float] = Field(0.3, ge=0.0, le=2.0, description="Штраф за частоту слов")
    presence_penalty: Optional[float] = Field(0.2, ge=0.0, le=2.0, description="Штраф за само наличие слов")
    thinking: Optional[bool] = False

    @field_validator('stop')
    @classmethod
    def validate_stop_sequences(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) > 10:
            raise ValueError("Слишком много стоп-последовательностей (макс. 10)")
        return v


class ProptionCreate(ProptionCustom, CustomCreate):
    preset: str = Field(..., min_length=2, max_length=50, pattern=r"^[A-ZА-Яa-zа-я0-9_-]+$")


class ProptionUpdate(ProptionCustom, CustomUpdate):
    preset: Optional[str] = Field(None, min_length=2, max_length=50, pattern=r"^[A-ZА-Яa-zа-я0-9_-]+$")


class ProptionRead(PkSchema, ProptionCreate, CustomRead):
    id: int


class PromptCreate(Subcategories, BaseModel, CustomCreate):
    """Модель для POST запроса: role и system_prompt обязательны"""
    role: str = Field(..., min_length=2, max_length=50, pattern=r"^[A-ZА-Яa-zа-я0-9_-]+$")
    system_prompt: str = Field(..., min_length=10)


class PromptUpdate(Subcategories, BaseModel, CustomUpdate):
    """Модель для PATCH запроса: все поля необязательны"""
    # Мы наследуем всё от Base, где поля уже Optional.
    # Поле role обычно не меняют через PATCH, но если нужно — добавим:
    role: Optional[str] = Field(None, min_length=2, max_length=50)
    system_prompt: Optional[str] = Field(None, min_length=10)

    # model_config = ConfigDict(extra='forbid')  # Запрещает передавать лишние поля


class PromptRead(Subcategories, PkSchema, PromptCreate, CustomRead):
    id: int


class LlmResponseSchema(BaseModel):
    """ получает на входе вложенный словарь LLM response и возвращает плоский словарь Ollama """
    model: str
    modified_at: datetime
    digest: Optional[str] = None
    size: Optional[int] = None
    # details: Optional[dict] = None
    parent_model: Optional[str] = None
    format: Optional[str] = None
    family: Optional[str] = None
    # families: Optional[List[str]] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None

    # @computed_field
    # @property
    # def size_gb(self) -> Optional[float]:
    #     """Возвращает размер модели в гигабайтах с округлением до 2 знаков."""
    #     if self.size is None:
    #         return None
    #     return round(self.size / (1024 ** 3), 2)

    @model_validator(mode='before')
    @classmethod
    def flatten_details(cls, data: dict) -> dict:
        # Извлекаем словарь details
        details = data.pop('details', {})
        # Объединяем основной словарь с содержимым details
        return {**data, **details}


class OllamaCreate(BaseModel):
    model: str
    modified_at: datetime
    digest: Optional[str] = None
    size: Optional[int] = None
    # details: Optional[dict] = None
    parent_model: Optional[str] = None
    format: Optional[str] = None
    family: Optional[str] = None
    # families: Optional[List[str]] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None


class OllamaUpdate(BaseModel):
    model: Optional[str] = None
    modified_at: Optional[datetime] = None
    digest: Optional[str] = None
    size: Optional[int] = None
    parent_model: Optional[str] = None
    format: Optional[str] = None
    family: Optional[str] = None
    parameter_size: Optional[str] = None
    quantization_level: Optional[str] = None


class OllamaRead(PkSchema, OllamaCreate):
    size: Optional[int] = Field(exclude=True)

    @computed_field
    @property
    def size_gb(self) -> Optional[float]:
        """Возвращает размер модели в гигабайтах с округлением до 2 знаков."""
        if self.size is None:
            return None
        return round(self.size / (1024 ** 3), 2)


class ISOLanguageCreate(BaseModel):
    iso_639_3: str
    iso_639_1: Optional[str] = None
    name_en: str
    name_ru: str


class ISOLanguageUpdate(BaseModel):
    iso_639_3: Optional[str] = None
    iso_639_1: Optional[str] = None
    name_en: Optional[str] = None
    name_ru: Optional[str] = None


class ISOLanguageRead(ISOLanguageCreate):
    id: int
