# app/mongodb/router.py
import io
from datetime import datetime, timezone
from typing import Optional

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, status, UploadFile
from fastapi.responses import StreamingResponse
# from app.auth.dependencies import get_current_active_user
from app.auth.dependencies import get_active_user_or_internal
from app.core.config.project_config import settings
from app.core.utils.common_utils import back_to_the_future
from app.mongodb.models import FileListResponse
from app.mongodb.service import ImageService
from app.core.cache import cache_key_builder, invalidate_cache

prefix = settings.MONGODB_PREFIX
subprefix = f"{settings.IMAGES_PREFIX}"
fileprefix = f"{settings.FILES_PREFIX}"
directprefix = f"{subprefix}/direct"
delta = (datetime.now(timezone.utc) - relativedelta(years=2))


# -----------------------
router = APIRouter(prefix=f"/{prefix}", tags=[f"{prefix}"], dependencies=[Depends(get_active_user_or_internal)])


@router.get(f'/{subprefix}', response_model=FileListResponse)
@cache_key_builder(prefix='mongodb_images', expire=300, key_params=["after_date", "page", "per_page"])
async def get_images_after_date(
    after_date: datetime = Query(delta, description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(100, ge=1, le=1000, description="Количество элементов на странице"),
    image_service: ImageService = Depends()
):
    """
    Получение постраничного списка id изображений, созданных после заданной даты.
    по умолчанию за 2 года до сейчас
    """
    try:
        # Проверяем, что дата не в будущем
        after_date = back_to_the_future(after_date)
        return await image_service.get_images_after_date(after_date, page, per_page)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(f'/{subprefix}list', response_model=dict)
@cache_key_builder(prefix='mongodb_images_list', expire=300, key_params=["after_date"])
async def get_images_list_after_date(
    after_date: datetime = Query(delta, description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
        image_service: ImageService = Depends()) -> dict:
    """
    список всех изображений в базе данных без страниц
    :return: возвращает список кортежей (id файла, имя файла)
    """
    try:
        # Проверяем, что дата не в будущем
        after_date = back_to_the_future(after_date)
        result = await image_service.get_images_list_after_date(after_date)
        return {a: b for b, a in result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(f'/{subprefix}/' + "{file_id}")  # , response_model=StreamingResponse)
@cache_key_builder(prefix='mongodb_image', expire=600, key_params=["file_id"])
async def download_image(
    file_id: str,
    image_service: ImageService = Depends()
):
    """
        Получение одного изображения по _id
    """
    image_data = await image_service.get_image(file_id)

    return StreamingResponse(
        io.BytesIO(image_data["content"]),
        media_type=image_data['content_type'],
        headers={"Content-Disposition": f"attachment; filename={image_data['filename']}"}
    )


@router.get(f'/{fileprefix}/' + "{filename}")
@cache_key_builder(prefix='mongodb_file', expire=600, key_params=["filename"])
async def download_file(
    filename: str,
    image_service: ImageService = Depends()
):
    """
        Получение одного изображения по имени файла
    """
    image_data = await image_service.get_image_by_filename(filename)

    return StreamingResponse(
        io.BytesIO(image_data["content"]),
        media_type=image_data['content_type'],
        headers={"Content-Disposition": f"attachment; filename={image_data['filename']}"}
    )


@router.post(f'/{subprefix}', response_model=dict)
@invalidate_cache(patterns=["mongodb_images:*", "mongodb_images_list:*", "mongodb_image:*", "mongodb_file:*"])
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    image_service: ImageService = Depends()
):
    """
    загрузка одного изображения в базу данных
    """
    file_id, filename = await image_service.upload_image(file, description)
    return {"id": file_id, 'file_name': filename, "message": "Image uploaded successfully"}


@router.post(f'/{directprefix}')
@invalidate_cache(patterns=["mongodb_images:*", "mongodb_images_list:*", "mongodb_image:*", "mongodb_file:*"])
async def direct_upload(image_service: ImageService = Depends()) -> dict:
    """
        импортирование рисунков из директории UPLOAD_DIR (см. .env file
        загрузка происходит в обход api. Для того что бы выполнить импорт нужно
        на сервере поместить файлы с изображениями в директорию UPLOAD_DIR.
        операция длительная - наберитесь терпения.
    """
    images = await image_service.direct_upload_image()
    # result = {b: a for a, b in images}
    return images


@router.delete(f'/{subprefix}/' + "{file_id}", response_model=dict)
@invalidate_cache(patterns=["mongodb_images:*", "mongodb_images_list:*", "mongodb_image:*", "mongodb_file:*"])
async def delete_image(
    file_id: str,
    image_service: ImageService = Depends()
):
    """
    удаление одного изображения по _id
    """
    success = await image_service.delete_image(file_id)  # , current_user.id)
    if success:
        return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
