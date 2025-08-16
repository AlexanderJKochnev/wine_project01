# app/core/schemas/dynamic_schema.py

""" Base Pydantic Model """
import sys
from typing import NewType, TypeVar, Optional, Union, Type, get_args
from pydantic import BaseModel, create_model, Field
from sqlalchemy.orm import DeclarativeMeta, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs

from app.core.utils.common_utils import get_model_fields_info

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)
PyModel = NewType("PyModel", BaseModel)

#  список полей которые доллны выводиться всегда (костыль)
# white_list: list = ['count_drink']


def create_drink_schema(model: Type[Union[AsyncAttrs, DeclarativeBase]],
                        schema_type: int = 0, include_list: list = [],
                        depth: int = 1, current_depth: int = 0
                        ) -> type[BaseModel]:
    """
    Создает Pydantic модель на основе SQLAlchemy модели с поддержкой отношений
    Args:
        sqlalchemy_model: Класс модели SQLAlchemy
        # schema_name: Имя для схемы (по умолчанию имя модели + 'Schema')
        # exclude_fields: Поля для исключения из схемы
        depth: Максимальная глубина вложенности (0 - только FK ID, 1 - базовые поля, 2+ - полные вложенные объекты)
        current_depth: Текущая глубина рекурсии (не задавать вручную)
    Read (0):   все поля кроме _id, pk, default_value <foreign>_id
    Create (1): все поля кроме _id, pk, default_value, foreign
    Update (2): все поля кроме _id, pk, default_value, foreign | все поля optional
    List:
    Delete:
    """
    # 1. define nem of schema
    model_name = model.__name__
    match schema_type:
        case 0:
            model_name = f'{model_name}Read'
        case 1:
            model_name = f'{model_name}Create'
        case 2:
            model_name = f'{model_name}Update'
        case _:
            model_name = f'{model_name}Base'
    # 2. Проверяем, существует ли уже такая модель в текущем модуле
    current_module = sys.modules[__name__]
    if hasattr(current_module, model_name):
        existing_model = getattr(current_module, model_name)
        if isinstance(existing_model, type) and issubclass(existing_model, BaseModel):
            return existing_model
    # 3. Получаем информацию о полях
    fields_info = get_model_fields_info(model, schema_type, include_list)

    # 4. Подготавливаем определения полей
    field_definitions = {}
    for field_name, field_data in fields_info.items():
        field_type = field_data.get('field_type')
        nullable = field_data.get('nullable', True)
        is_foreign = field_data.get('foreign')

        if is_foreign:
            print(f'{field_type=} {type(field_type)=} {depth=} {current_depth=}')
            print(f'{field_type.__name__=}')
        # 4.1. Обработка foreign-полей
        if is_foreign and current_depth < depth:
            if field_type.__name__ == 'List':  # One-to-Many
                # Получаем тип связанной модели
                related_model = get_args(field_type)[0]
                if related_model:
                    related_model = next(iter(related_model))
                if depth == 1:  # Только ID и имя
                    # field_definitions[f"{field_name}_ids"] = (list[int], Field(default_factory=list))
                    # field_definitions[f"{field_name}"] = (list[str], Field(default_factory=list))
                    continue
                else:  # Полные объекты
                    related_schema = create_drink_schema(related_model,
                                                         schema_type=0,
                                                         current_depth=current_depth + 1
                                                         )
                    py_type = list[related_schema]
            else:  # Many-to-One
                related_model = field_type
                if current_depth >= depth:  # Только ID
                    py_type = int
                else:  # Полный объект или имя
                    if depth == 101:  # Только имя
                        py_type = str
                    else:  # Полный объект
                        related_schema = create_drink_schema(related_model,
                                                             schema_type=0,
                                                             current_depth=current_depth + 1
                                                             )
                        py_type = related_schema
        else:
            # Определяем тип с учетом nullable
            py_type = Optional[field_type] if nullable else field_type

        # Параметры Field
        field_params = {'default': None if nullable else ..., 'nullable': nullable}

        # Добавляем default значение если оно есть (default быть не должно)
        # if len(field_data) > 5 and field_data[4]:  # has_default и default_value
        #     field_params['default'] = field_data[5]
        #     field_params['default_factory'] = None

        # Для отношений (foreign=True) делаем поле Optional
        # if len(field_data) > 3 and field_data[3]:  # foreign=True
        if is_foreign:
            py_type = Optional[py_type]
            # py_type = Optional[py_type] if not py_type._name == 'Optional' else py_type

        # Создаем поле
        field_definitions[field_name] = (py_type, Field(**field_params))
    """
    if schema_type == 0:
        print(f'-------{model_name}----------------------')
        for key, val in field_definitions.items():
            print(f'{key}:: {val}')
    """
    # Создаем модель с дополнительными настройками
    Schema = create_model(model_name,
                          # model_config=ConfigDict(rom_attributes=True, arbitrary_types_allowed=True),
                          __config__={'arbitrary_types_allowed': True, 'from_attributes': True},
                          **field_definitions)
    return Schema
