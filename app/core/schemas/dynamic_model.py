# app/cor/schemas/dynamic_model.py
from typing import Optional, Type  # , Dict, Any
from pydantic import BaseModel, Field, create_model
from sqlalchemy import String, Text, Unicode, UnicodeText


def create_search_model(model_class: Type) -> Type[BaseModel]:
    """
    Динамически создает модель поиска на основе SQLAlchemy модели
    """
    fields = {}

    # Получаем текстовые поля из модели
    for column in model_class.__table__.columns:
        # print(f'{column}, {column.type}')
        if isinstance(column.type, (String, Text, Unicode, UnicodeText)):
            field_name = column.name
            fields[field_name] = (Optional[str],
                                  Field(None, description=f"Поиск по полю '{field_name}'"))
    if not fields:
        raise ValueError(f"Модель {model_class.__name__} не содержит текстовых полей")

    # Создаем динамическую модель
    model_name = f"{model_class.__name__}SearchRequest"
    return create_model(model_name, **fields, __base__=BaseModel)

# Пример использования:
# UserSearchRequest = create_search_model(User, SearchBaseRequest)
# ProductSearchRequest = create_search_model(Product, SearchBaseRequest)
