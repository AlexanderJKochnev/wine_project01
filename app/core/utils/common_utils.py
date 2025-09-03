# app/core/common_utils.py
# some useful utilits

from pathlib import Path
from typing import Dict, List, TypeVar
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import DeclarativeMeta, RelationshipProperty
from sqlalchemy import inspect
# from sqlalchemy.sql.sqltypes import String, Text, Boolean
from sqlalchemy import String, Text, Unicode, UnicodeText, Boolean
from sqlalchemy.dialects.postgresql import CITEXT  # если используешь PostgreSQL


ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


def strtolist(data: str, delim: str = ',') -> List[str]:
    """ строка с разделителями в список"""
    if isinstance(data, str):
        return [a.strip() for a in data.split(delim)]
    else:
        return []


def sort_strings_by_alphabet_and_length(strings: List[str]) -> List[str]:
    """
    Сортирует список строк сначала по алфавиту, затем по длине строки.

    Args:
        strings: Список строк для сортировки

    Returns:
        Отсортированный список строк
    """
    return sorted(strings, key=lambda s: (s.lower(), len(s)))


def get_path_to_root(name: str = '.env'):
    """
        get path to fiile in root directory
    """
    for k in range(5):
        env_path = Path(__file__).resolve().parents[k] / name
        if env_path.exists():
            break
    else:
        env_path = None
        raise Exception('environment file is not found')
    return env_path


def get_searchable_fields(model: type) -> Dict[str, type]:
    """
    СЛОВАРЬ ПОЛЕЙ ПО КОТОРЫМ МОЖНО ОСУЩЕВЛЯТЬ ПОИСК
    Возвращает словарь: {field_name: field_type}
    включая:
    - простые поля модели
    - поля из relationships в формате: rel_name_field_name
    """
    mapper = model.__mapper__
    fields = {}

    # 1. Простые поля
    for column in mapper.columns:
        if column.primary_key or not hasattr(column.type, "python_type"):
            continue
        fields[column.name] = column.type.python_type

    # 2. Поля из relationships
    for rel_name, relationship in mapper.relationships.items():
        if relationship.uselist:  # one-to-many — ищем по связанным объектам
            continue  # пропускаем списки, ищем только many-to-one / one-to-one

        remote_model = relationship.entity.entity
        remote_mapper = remote_model.__mapper__

        for col in remote_mapper.columns:
            if col.primary_key:
                continue
            field_name = f"{rel_name}_{col.name}"
            fields[field_name] = col.type.python_type

    return fields


def apply_relationship_loads(stmt: Select, model: DeclarativeMeta) -> Select:
    """
    Автоматически добавляет .options(selectinload(...)) для всех many-to-one relationships.
    Используется при детальном чтении.
    """
    mapper = model.__mapper__
    for rel_name, relationship in mapper.relationships.items():
        if relationship.uselist:
            continue  # skip one-to-many (можно расширить при необходимости)
        stmt = stmt.options(selectinload(getattr(model, rel_name)))
    return stmt


def get_model_fields_info(model, schema_type: int = 0, include_list: list = []) -> dict:
    """
    Возвращает информацию о полях модели:
    - field_type: тип поля
    - nullable: может ли быть NULL (bool)
    - primary_key: является ли первичным ключом (bool)
    - foreign: является ли внешним ключом (bool)
    - has_default: есть ли значение по умолчанию (bool)
    - # default_value: само значение по умолчанию (если есть)
    schema_type:
    Read (0):   все поля кроме _id, pk, default_value
    Create (1): все поля кроме _id, pk, default_value, foreign
    Update (2): все поля кроме _id, pk, default_value, foreign | все поля optional
    include_list: имена полей которые должны быть включены обязательно
    """
    defval, pk, _id, foreign, updatable = False, False, False, True, True,
    match schema_type:
        case 0:  # Read
            pk, _id, defval, foreign = True, True, True, False
        case 1:  # Create
            pk, defval, foreign = True, True, False
        case 2:  # Update
            pk, defval, foreign, updatable = True, True, False, False
        case _:  # All
            pass

    fields_info = {}

    # 1. Стандартные колонки через __table__
    if hasattr(model, "__table__") and model.__table__ is not None:
        for col in model.__table__.columns:
            field_type = getattr(col.type, "python_type", None)
            if field_type is None:
                field_type = type(col.type)

            # Определяем наличие и значение по умолчанию
            has_default = False
            # default_value = None

            if col.default is not None:
                has_default = True
                # if col.default.is_scalar:
                #     default_value = col.default.arg
                # elif col.default.is_callable:
                #     default_value = f"<callable: {col.default.callable.__name__}>"
            elif col.server_default is not None:
                has_default = True
                # default_value = f"<server_default: {str(col.server_default)}>"
            # defval, pk, _id, foreign, updatable
            if all((pk, col.primary_key, col.name not in include_list)):
                continue
            if all((defval, has_default, col.name not in include_list)):
                continue
            if all((_id, col.name.endswith('_id'), col.name not in include_list)):
                continue
            xnullable = col.nullable if updatable else True
            fields_info[col.name] = {'field_type': field_type,
                                     'nullable': xnullable,
                                     'primary_key': col.primary_key,
                                     'foreign': False,  # Это не foreign key
                                     'has_default': has_default}  # , default_value)
    # 2. Relationships через маппер
    if all((hasattr(model, "__mapper__"), foreign)):
        for rel in model.__mapper__.relationships:
            direction = rel.direction.name
            target = rel.entity.class_  # .__name__
            # print(f'{target=}, {type(target)=}')
            if direction == "ONETOMANY":
                field_type = List[{target}]
                is_nullable = True
            else:  # MANYTOONE
                field_type = target
                is_nullable = True
                for local_col in rel.local_columns:
                    if hasattr(local_col, "nullable"):
                        is_nullable = local_col.nullable
                        break
            xnullable = is_nullable if updatable else True
            fields_info[rel.key] = {'field_type': field_type,
                                    'nullable': xnullable,
                                    'primary_key': False,
                                    'foreign': True,  # Это foreign key
                                    'has_default': False}  # , default_value)

    return fields_info


def print_model_schema(model, title=None):
    """
    Выводит схему модели в читаемом виде.
    """
    # schema = generate_model_schema(model)
    name = title or model.__name__
    print(f"\n📊 Схема модели: {name}")
    print("-" * 50)
    for field, info in model.items():
        type_str = info["type"]
        null_str = "NULL" if info["nullable"] else "NOT NULL"
        extra = ""
        if info.get("relation"):
            extra = f" 🔗 {info['direction']} → {info['back_populates']}"
        if info.get("default"):
            extra += f" (default={info['default']})"
        print(f"{field:20} : {type_str:12} | {null_str:8}{extra}")


def get_model_fields(model: ModelType, exclude_columns: List[str] = [],
                     list_view: bool = False,
                     detail_view: bool = False) -> List[str]:
    mapper = inspect(model)
    columns = []

    # Группируем поля по категориям
    str_fields = []    # текстовые обязательные поля
    str_null_fields = []    # текстовые необязательные поля
    bool_fields = []
    rel_fields = []     # relation fields
    memo_fields = []    # memo fields
    other_fields = []   # остальные поля
    other_null_fields = []

    for attr in mapper.attrs:
        if attr.key in exclude_columns:
            continue

        if isinstance(attr, RelationshipProperty):
            if attr.direction.name == "MANYTOONE":
                rel_fields.append(attr.key)
            continue

        if hasattr(attr, "columns"):
            col = attr.columns[0]
            # Пропускаем поля с default
            if col.default is not None:  # or col.autoincrement:
                continue
            # Получаем тип поля
            col_type = col.type.__class__ if hasattr(col.type, '__class__') else type(col.type)
            if issubclass(col_type, Text):
                memo_fields.append(attr.key)
                continue
            if issubclass(col_type, Boolean):
                bool_fields.append(attr.key)
                continue
            if issubclass(col_type, String):
                if not col.nullable:
                    str_fields.append(attr.key)
                    continue
                str_null_fields.append(attr.key)
                continue
            # Другие типы (Integer и т.д.)
            if not col.nullable:
                other_fields.append(attr.key)
                continue
            other_null_fields.append(attr.key)
    """
    print(f'{str_fields=}')
    print(f'{str_null_fields=}')
    print(f'{bool_fields=}')
    print(f'{rel_fields=}')
    print(f'{other_fields=}')
    print(f'{other_null_fields=}')
    print(f'{memo_fields=}')
    """
    # Формируем итоговый порядок
    columns.extend(sort_strings_by_alphabet_and_length(str_fields))
    columns.extend(sort_strings_by_alphabet_and_length(str_null_fields))
    if not list_view:
        columns.extend(sort_strings_by_alphabet_and_length(other_fields))  # Добавляем другие типы после String
        columns.extend(sort_strings_by_alphabet_and_length(other_null_fields))
        columns.extend(sort_strings_by_alphabet_and_length(bool_fields))
        columns.extend(sort_strings_by_alphabet_and_length(rel_fields))
        columns.extend(sort_strings_by_alphabet_and_length(memo_fields))
    if detail_view:
        columns = [a for a in columns if all((not a.endswith('_id'), a != 'image_path'))]
    return columns


def get_text_model_fields(model: ModelType) -> List[str]:
    # Список типов, которые считаем "текстовыми"
    text_types = (String, Text, Unicode, UnicodeText, CITEXT)
    return [col.name for col in model.__table__.columns if isinstance(col.type, text_types)]
