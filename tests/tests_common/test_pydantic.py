# tests/test_pydantic.py
"""
тестирование метода sqlalchemy_to_pydantic_post
конвертация sqlalchemy model to pydantic model
"""

import pytest
from decimal import Decimal
from typing import Optional, get_type_hints
from sqlalchemy import Integer, String, Text, Float, Numeric, ForeignKey, inspect
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic import BaseModel

# Импортируйте вашу функцию генерации
from app.core.utils.pydantic_utils import sqlalchemy_to_pydantic_post  # замените your_module на реальный путь


# Тестовые модели SQLAlchemy
class Base(DeclarativeBase):
    pass


class TestCategory(Base):
    __tablename__ = "test_categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int] = mapped_column(ForeignKey("test_categories.id"), nullable=True)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    optional_int: Mapped[int] = mapped_column(Integer, nullable=True)


class TestProduct(Base):
    __tablename__ = "test_products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("test_categories.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(String, nullable=False)  # будет исключено


def test_sqlalchemy_to_pydantic_post_basic():
    """Тест базового соответствия полей"""
    # Генерируем Pydantic модель
    CategoryCreate = sqlalchemy_to_pydantic_post(TestCategory)

    # Проверяем, что это подкласс BaseModel
    assert issubclass(CategoryCreate, BaseModel)
    assert CategoryCreate.__name__ == "TestCategoryCreate"

    # Получаем аннотации типов
    pydantic_annotations = get_type_hints(CategoryCreate, include_extras=True)

    # Получаем колонки SQLAlchemy модели
    mapper = inspect(TestCategory)
    sqla_columns = {col.key: col for col in mapper.columns}

    # Поля, которые должны быть в Pydantic модели (исключая служебные)
    expected_fields = {"name", "description", "parent_id", "weight", "price", "optional_int"}
    actual_fields = set(pydantic_annotations.keys())

    assert actual_fields == expected_fields, f"Expected fields {expected_fields}, got {actual_fields}"

    # Проверяем типы каждого поля
    assert pydantic_annotations["name"] == str
    assert pydantic_annotations["description"] == Optional[str]
    assert pydantic_annotations["parent_id"] == Optional[int]
    assert pydantic_annotations["weight"] == float
    assert pydantic_annotations["price"] == Decimal
    assert pydantic_annotations["optional_int"] == Optional[int]


def test_sqlalchemy_to_pydantic_post_foreign_keys():
    """Тест обработки foreign key полей"""
    ProductCreate = sqlalchemy_to_pydantic_post(TestProduct)

    pydantic_annotations = get_type_hints(ProductCreate, include_extras=True)

    # Проверяем, что category_id присутствует и имеет тип int (не Optional, т.к. nullable=False)
    assert "category_id" in pydantic_annotations
    assert pydantic_annotations["category_id"] == int

    # Проверяем, что служебные поля исключены
    assert "id" not in pydantic_annotations
    assert "created_at" not in pydantic_annotations


def test_sqlalchemy_to_pydantic_post_exclude_fields():
    """Тест кастомного исключения полей"""
    # Исключаем дополнительное поле
    CategoryCreate = sqlalchemy_to_pydantic_post(
        TestCategory, exclude_fields={"id", "created_at", "weight"}
    )

    pydantic_annotations = get_type_hints(CategoryCreate, include_extras=True)

    # weight должно быть исключено
    assert "weight" not in pydantic_annotations
    # остальные поля должны быть на месте
    assert "name" in pydantic_annotations
    assert "description" in pydantic_annotations


def test_sqlalchemy_to_pydantic_post_optional_fields():
    """Тест принудительного making полей optional"""
    CategoryCreate = sqlalchemy_to_pydantic_post(
        TestCategory, optional_fields={"name", "weight"}  # даже если nullable=False
    )

    pydantic_annotations = get_type_hints(CategoryCreate, include_extras=True)

    # name и weight должны быть Optional, несмотря на nullable=False
    assert pydantic_annotations["name"] == Optional[str]
    assert pydantic_annotations["weight"] == Optional[float]

    # price остается обязательным (nullable=False и не в optional_fields)
    assert pydantic_annotations["price"] == Decimal


def test_sqlalchemy_to_pydantic_post_validation():
    """Тест валидации данных через Pydantic модель"""
    CategoryCreate = sqlalchemy_to_pydantic_post(TestCategory)

    # Валидные данные
    valid_data = {"name": "Electronics", "description": "Electronic devices", "parent_id": 1, "weight": 1.5,
                  "price": Decimal("99.99"), "optional_int": 42}

    model = CategoryCreate(**valid_data)
    assert model.name == "Electronics"
    assert model.description == "Electronic devices"
    assert model.parent_id == 1
    assert model.weight == 1.5
    assert model.price == Decimal("99.99")
    assert model.optional_int == 42

    # Данные без optional полей
    minimal_data = {"name": "Books", "weight": 0.5, "price": Decimal("19.99")}

    model2 = CategoryCreate(**minimal_data)
    assert model2.name == "Books"
    assert model2.description is None
    assert model2.parent_id is None
    assert model2.optional_int is None

    # Невалидные данные - должно вызвать ошибку
    with pytest.raises(ValueError):
        CategoryCreate(
            name=123,  # должно быть строкой
            weight=1.5, price=Decimal("10.00")
        )


def test_sqlalchemy_to_pydantic_post_model_dump():
    """Тест совместимости с model_dump() для создания SQLAlchemy объекта"""
    CategoryCreate = sqlalchemy_to_pydantic_post(TestCategory)

    data = {"name": "Test Category", "description": "Test description", "parent_id": 5, "weight": 2.3,
            "price": Decimal("50.00"), "optional_int": None}

    pydantic_model = CategoryCreate(**data)

    # Преобразуем в словарь для создания SQLAlchemy объекта
    sqla_kwargs = pydantic_model.model_dump(exclude_unset=True)

    # Проверяем, что все ключи корректны
    expected_keys = {"name", "description", "parent_id", "weight", "price", "optional_int"}
    assert set(sqla_kwargs.keys()) == expected_keys

    # Проверяем значения
    assert sqla_kwargs["name"] == "Test Category"
    assert sqla_kwargs["parent_id"] == 5
    assert sqla_kwargs["weight"] == 2.3
    assert sqla_kwargs["price"] == Decimal("50.00")


def test_sqlalchemy_to_pydantic_post_empty_model():
    """Тест модели без полей (кроме исключаемых)"""

    class EmptyModel(Base):
        __tablename__ = "empty"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        created_at: Mapped[str] = mapped_column(String)

    EmptyCreate = sqlalchemy_to_pydantic_post(EmptyModel)
    pydantic_annotations = get_type_hints(EmptyCreate, include_extras=True)

    # Должна быть пустая модель
    assert len(pydantic_annotations) == 0


if __name__ == "__main__":
    pytest.main([__file__])
