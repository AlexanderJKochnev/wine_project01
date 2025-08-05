# app/core/utils.py
# some useful utilits

from pathlib import Path
from typing import Dict


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
    СЛОВАРЬ ПОЛЕ ПО КОТОРЫМ МОЖНО ОСУЩЕВЛЯТЬ ПОИСК
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
