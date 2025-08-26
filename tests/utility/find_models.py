# tests/utility/find_models.py

import sys
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
import pytest
import asyncio
import inspect
from typing import Dict, List, Any, Type, Set
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import MetaData
from faker import Faker
import tempfile
from pathlib import Path
from httpx import AsyncClient
import importlib
import sys
from fastapi import FastAPI
from fastapi.routing import APIRoute, APIRouter
from app.main import app, get_db


def find_sqlalchemy_bases():
    """Находит все классы, унаследованные от DeclarativeBase."""
    bases = []
    for module in list(sys.modules.values()):
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, DeclarativeBase)
                and obj != DeclarativeBase
                and hasattr(obj, "registry")  # у Base есть registry
            ):
                bases.append(obj)
    return bases


def discover_models():
    """Находит все SQLAlchemy ORM-модели в проекте."""
    models = set()
    bases = find_sqlalchemy_bases()
    for Base in bases:
        for model in Base.registry._class_registry.values():
            # Фильтруем только те, у кого есть таблица (реальные модели)
            if hasattr(model, "__table__"):
                models.add(model)
    return list(models)


def discover_schemas():
    """Автоматически обнаруживает все схемы в приложении"""
    schemas = {}

    # Ищем схемы в модулях app.schemas
    try:
        schemas_module = importlib.import_module('app.schemas')
        for name, obj in inspect.getmembers(schemas_module):
            if inspect.isclass(obj) and issubclass(obj, BaseModel):
                # Определяем тип схемы по имени
                if name.endswith('Create'):
                    model_name = name[:-6]
                    if model_name not in schemas:
                        schemas[model_name] = {}
                    schemas[model_name]['create'] = obj
                elif name.endswith('Update'):
                    model_name = name[:-6]
                    if model_name not in schemas:
                        schemas[model_name] = {}
                    schemas[model_name]['update'] = obj
                elif name.endswith('Read'):
                    model_name = name[:-4]
                    if model_name not in schemas:
                        schemas[model_name] = {}
                    schemas[model_name]['read'] = obj
    except ImportError:
        pass
    return schemas


def discover_schemas2(app: FastAPI = app) -> dict[str, type[BaseModel]]:
    """
    Извлекает все Pydantic-модели (и request, и response) из всех маршрутов FastAPI.
    Поддерживает все HTTP-методы (GET, POST, PUT и т.д.).
    Возвращает словарь: {имя_модели: класс_модели}.
    """
    models: dict[str, type[BaseModel]] = {}

    def extract_from_router(router: APIRouter):
        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue

            # 1. Response model
            if route.response_model:
                model = route.response_model
                if issubclass(model, BaseModel) and model.__name__ not in models:
                    models[model.__name__] = model

            # 2. Request model (из dependencies, параметров, тела)
            # FastAPI хранит зависимости и аннотации, но тело (Body) — в зависимости от параметров
            for param in route.dependant.body_params:
                # param — это объект ModelField, его тип — Pydantic-модель
                if hasattr(param, "annotation") and issubclass(param.annotation, BaseModel):
                    model = param.annotation
                    if model.__name__ not in models:
                        models[model.__name__] = model

    extract_from_router(app.router)
    return models
