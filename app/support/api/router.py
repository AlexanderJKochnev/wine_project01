# app/support/api/router.py
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from app.auth.dependencies import get_current_active_user
from app.core.config.project_config import settings
from app.core.utils.common_utils import back_to_the_future
from app.mongodb.models import JustListResponse
from app.mongodb.service import ImageService

# from app.auth.dependencies import get_current_user, User
prefix = settings.API_PREFIX
router = APIRouter(prefix=f"/{prefix}", tags=[f"{prefix}"])
# subprefix = settings.IMAGES_PREFIX
# fileprefix = settings.FILES_PREFIX
now = datetime.now(timezone.utc).isoformat()


@router.get("", response_model=JustListResponse)
async def get_images_after_date_nopage(
    after_date: datetime = Query((datetime.now(timezone.utc) - relativedelta(years=2)).isoformat(),
                                 description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
    image_service: ImageService = Depends()
):
    """
    Получить изображения, созданные после указанной даты
    """
    try:
        # Проверяем, что дата не в будущем
        after_date = back_to_the_future(after_date)
        return await (image_service.get_images_list_after_date(after_date))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/paging", response_model=JustListResponse)
async def get_images_after_date(
    after_date: datetime = Query((datetime.now(timezone.utc) - relativedelta(years=2)).isoformat(),
                                 description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(100, ge=1, le=1000, description="Количество элементов на странице"),
    image_service: ImageService = Depends()
):
    """
    Получить изображения, созданные после указанной даты
    """
    try:
        # Проверяем, что дата не в будущем
        after_date = back_to_the_future(after_date)
        return await (image_service.get_images_list_after_date(after_date, page, per_page))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
