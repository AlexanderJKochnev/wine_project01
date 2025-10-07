# app/mongodb/router.py
import io
from datetime import datetime, timezone
from typing import Optional

from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, status, UploadFile
from fastapi.responses import StreamingResponse
from app.auth.dependencies import get_current_active_user
from app.core.config.project_config import settings
from app.core.utils.common_utils import back_to_the_future
from app.mongodb.models import FileListResponse
from app.mongodb.service import ImageService

# from app.auth.dependencies import get_current_user, User
prefix = settings.MONGODB_PREFIX
router = APIRouter(prefix=f"/{prefix}", tags=[f"{prefix}"], dependencies=[Depends(get_current_active_user)])
subprefix = f"{settings.IMAGES_PREFIX}"
fileprefix = f"{settings.FILES_PREFIX}"
directprefix = f"{subprefix}/direct"


# now = datetime.now(timezone.utc).isoformat()
delta = (datetime.now(timezone.utc) - relativedelta(years=2))
# delta = (datetime.now(timezone.utc) - relativedelta(years=2)).isoformat()


@router.post(f'/{subprefix}', response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    image_service: ImageService = Depends()
):
    """
    загрузка изображения в базу данных
    """
    file_id, filename = await image_service.upload_image(file, description)
    return {"id": file_id, 'file_name': filename, "message": "Image uploaded successfully"}


@router.post(f'/{directprefix}')
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


@router.get(f'/{subprefix}', response_model=FileListResponse)
async def get_images_after_date(
    after_date: datetime = Query(delta, description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
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
        return await image_service.get_images_after_date(after_date, page, per_page)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(f'/{subprefix}/' + "{file_id}")  # , response_model=StreamingResponse)
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


@router.delete(f'/{subprefix}/' + "{file_id}", response_model=dict)
async def delete_image(
    file_id: str,
    # current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    success = await image_service.delete_image(file_id)  # , current_user.id)
    if success:
        return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


@router.get(f'/{subprefix}list', response_model=dict)
async def get_images_list_after_date(
    after_date: datetime = Query(delta, description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
        image_service: ImageService = Depends()) -> dict:
    """
    Получить список id изображений, созданные после указанной даты
    """
    try:
        # Проверяем, что дата не в будущем
        after_date = back_to_the_future(after_date)
        result = await image_service.get_images_list_after_date(after_date)
        return {a: b for b, a in result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
