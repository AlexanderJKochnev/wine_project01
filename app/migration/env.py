# import asyncio
# flake8: NOQA: F401, E402
import re
from logging.config import fileConfig

# from sqlalchemy import pool
# from sqlalchemy.engine import Connection
# from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic.autogenerate import Rewriter
from alembic.operations import ops

from alembic import context
import sys
from os.path import dirname, abspath
from app.core.config.database.db_sync import engine_sync as app_engine

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from app.core.models.base_model import Base
# -------model import----------------
from app.support.drink.model import Drink
from app.support.country.model import Country
from app.support.category.model import Category
from app.support.customer.model import Customer
from app.support.warehouse.model import Warehouse
from app.support.food.model import Food
from app.support.superfood.model import Superfood
from app.support.item.model import Item
from app.support.region.model import Region
from app.support.sweetness.model import Sweetness
from app.auth.models import User
from app.core.config.database.db_config import settings_db
from app.support.drink.model import DrinkFood
from app.support.subregion.model import Subregion
from app.support.subcategory.model import Subcategory
from app.support.parser.model import Name, Image, Code, Rawdata, Registry
from app.support.field_keys.model import FieldKey
from app.support.ollama.model import Ollama, Prompt, ISOLanguage, Proption, WriterRule
from app.support.lwin.model import Lwin
from app.support import Source
from app.support.producer.model import Producer, ProducerTitle
from app.support.parcel.model import Site, Parcel
from app.support.tasting.model import Glassware, TastingNote, Scale, Body, BaseIngredient
from app.support.vllm.model import TranslateRawData, TmpTranslate, TranslateHelper

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

section = config.config_ini_section
config.set_section_option(section, "POSTGRES_HOST", settings_db.POSTGRES_HOST)
config.set_section_option(section, "POSTGRES_PORT", settings_db.POSTGRES_PORT)
config.set_section_option(section, "POSTGRES_USER", settings_db.POSTGRES_USER)
config.set_section_option(section, "POSTGRES_DB", settings_db.POSTGRES_DB)
config.set_section_option(section, "POSTGRES_PASSWORD",
                          settings_db.POSTGRES_PASSWORD)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

#------------------
# 1. Определяем функцию-критерий отбора проблемных индексов
def is_tracked_problematic_index(name_obj: str) -> bool:
    if not name_obj:
        return False
    
    name = str(name_obj)
    # Критерий 1: Начало названия индекса (добавляйте сюда новые префиксы при необходимости)
    target_prefixes = ("uq_idx_", "ix_translatehelper_")
    starts_correctly = any(name.startswith(prefix) for prefix in target_prefixes)
    
    # Критерий 2: Конец названия содержит версию, например: _v1, _v2, _v12
    has_version_suffix = bool(re.search(r'_v\d+$', name))
    
    return starts_correctly and has_version_suffix


def filter_false_positive_indexes(context, revision, directives):
    """
    Анализирует весь список сгенерированных команд автогенерации.
    Если для одного и того же версионированного индекса найдены и DROP, и CREATE,
    они удаляются как ложное срабатывание. Одиночные команды пропускаются.
    """
    # Директивы автогенерации обычно лежат в первом элементе списка
    if not directives:
        return
        
        # Alembic может передавать директивы списком. Берём первый элемент, если это список.
    directive = directives[0] if isinstance(directives, list) else directives
    
    if not hasattr(directive, "upgrade_ops") or directive.upgrade_ops is None:
        return
    
    upgrade_ops = directive.upgrade_ops.ops
    
    # Собираем чистые строковые имена индексов, которые планируется УДАЛИТЬ
    dropped_indexes = {str(op.index_name) for op in upgrade_ops if
            isinstance(op, ops.DropIndexOp) and is_tracked_problematic_index(op.index_name)}
    
    # Собираем чистые строковые имена индексов, которые планируется СОЗДАТЬ
    created_indexes = {str(op.index_name) for op in upgrade_ops if
            isinstance(op, ops.CreateIndexOp) and is_tracked_problematic_index(op.index_name)}
    
    # Находим пересечение (индексы, которые попали в ложный цикл DROP + CREATE)
    false_positives = dropped_indexes.intersection(created_indexes)
    
    if false_positives:
        # Очищаем список операций от парных команд для этих индексов
        filtered_ops = [op for op in upgrade_ops if
                not (isinstance(op, (ops.DropIndexOp, ops.CreateIndexOp)) and str(op.index_name) in false_positives)]
        # Перезаписываем операции Alembic
        directive.upgrade_ops.ops = filtered_ops

#------------------
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Обязательно подключаем наш writer в директивы ревизии
        process_revision_directives=filter_false_positive_indexes,
        # end injection
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if name.startswith("auth_"):
            return False
    return True


def run_migrations_online():
    connectable = app_engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Обязательно подключаем наш writer в директивы ревизии
            process_revision_directives=filter_false_positive_indexes,
            # end injection
            include_object=include_object,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()

"""
def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""
