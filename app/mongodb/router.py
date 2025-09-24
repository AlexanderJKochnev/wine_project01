# app/mongodb/router.py
""" этот роутер только для целеей тестирования в dev отключить, заходить через
    postgres related routers
    вместо get_current_user - drink_id
"""
import io
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, status, UploadFile
from fastapi.responses import StreamingResponse
from app.mongodb.models import FileListResponse
from app.mongodb.service import ImageService

# from app.auth.dependencies import get_current_user, User

router = APIRouter(prefix="/mongodb", tags=["mongodb"])


@router.post("/images/", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    # current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    """
    загрузка изображения в базу данных
    """
    content = await file.read()
    file_id = await image_service.upload_image(file.filename, content, description)  # , current_user.id)
    return {"id": file_id, "message": "Image uploaded successfully"}


@router.get("/images/", response_model=FileListResponse)
async def get_images_after_date(
    after_date: datetime = Query(..., description="Дата в формате ISO 8601 (например, 2024-01-01T00:00:00Z)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(100, ge=1, le=1000, description="Количество элементов на странице"),
    image_service: ImageService = Depends()
):
    """
    Получить изображения, созданные после указанной даты
    """
    try:
        # Проверяем, что дата не в будущем
        if after_date > datetime.utcnow():
            raise HTTPException(
                status_code=400, 
                detail="Date cannot be in the future"
            )
        
        return await image_service.get_images_after_date(after_date, page, per_page)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/images/{file_id}")
async def download_image(
    file_id: str,
    # current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    image_data = await image_service.get_image(file_id
                                               # , current_user.id
                                               )
    return StreamingResponse(
        io.BytesIO(image_data["content"]),
        media_type="image/jpeg",
        headers={"Content-Disposition": f"attachment; filename={image_data['filename']}"}
    )


@router.delete("/images/{file_id}", response_model=dict)
async def delete_image(
    file_id: str,
    # current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    success = await image_service.delete_image(file_id)  # , current_user.id)
    if success:
        return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")
