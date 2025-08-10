from fastapi import Depends, Query, Request
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List  # get_type_hints
from app.core.utils import get_searchable_fields
from app.core.config.database.db_noclass import get_db
from app.core.config.project_config import get_paging
"""
   создание динамического роутера для поиска NOT IMPLEMENTED
"""


paging = get_paging


def create_find_router(repo, model, ReadSchema):
    searchable_fields = get_searchable_fields(model)

    # Создаём функцию-роутер
    async def find_handler(
        request: Request,
        db: AsyncSession = Depends(get_db),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, le=100),
    ):
        # Собираем фильтры из query_params
        filters = {}
        for key, value in request.query_params.items():
            if key in ["skip", "limit"]:
                continue
            # Поддержка модификаторов: name__contains
            base_field = key.split("__")[0]
            if "__" in key:
                op = key.split("__")[1]
                if op == "contains":
                    filters[key] = value
            elif base_field in searchable_fields:
                filters[key] = value

        # Передаём в репозиторий
        items = await repo.find(db, skip=skip, limit=limit, **filters)
        return [
            ReadSchema.model_validate(item, from_attributes=True)
            for item in items
        ]

    # Генерируем OpenAPI-документацию вручную
    parameters = [
        {
            "name": field_name,
            "in": "query",
            "required": False,
            "schema": {"type": "string"},  # можно улучшить по типу
            "description": f"Filter by {field_name}"
        }
        for field_name in searchable_fields
    ] + [
        {
            "name": f"{field_name}__contains",
            "in": "query",
            "required": False,
            "schema": {"type": "string"},
            "description": f"Filter by LIKE %value% on {field_name}"
        }
        for field_name in searchable_fields
    ]

    # Создаём маршрут с кастомной OpenAPI-секцией
    route = APIRoute(
        path="/find/",
        endpoint=find_handler,
        methods=["GET"],
        response_model=List[ReadSchema],
        name=f"Find {model.__name__}",
        description=f"Search {model.__name__} by any field (direct and relationship fields)",
        openapi_extra={
            "parameters": parameters
        }
    )

    return route
