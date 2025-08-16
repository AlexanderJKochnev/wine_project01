# app/core/utils.py
# some useful utilits

from pathlib import Path
from typing import Dict, List
from sqlalchemy.orm import selectinload
# from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.selectable import Select
from sqlalchemy.orm import DeclarativeMeta


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


#  список полей которые доллны выводиться всегда (костыль)
white_list: list = ['count_drink']


def get_model_fields_info(model, schema_type: int = 0, include_list: list = white_list) -> dict:
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
