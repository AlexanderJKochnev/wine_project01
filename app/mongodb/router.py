# app/mongodb/router.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io

from app.mongodb.service import ImageService, DocumentService
from app.auth.dependencies import get_current_user, User

router = APIRouter(prefix="/mongodb", tags=["mongodb"])


@router.post("/images/", response_model=dict)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    content = await file.read()
    file_id = await image_service.upload_image(file.filename, content, description, current_user.id)
    return {"id": file_id, "message": "Image uploaded successfully"}


@router.get("/images/", response_model=List[dict])
async def get_user_images(
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    return await image_service.get_user_images(current_user.id)


@router.get("/images/{file_id}")
async def download_image(
    file_id: str,
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    image_data = await image_service.get_image(file_id, current_user.id)
    return StreamingResponse(
        io.BytesIO(image_data["content"]),
        media_type="image/jpeg",
        headers={"Content-Disposition": f"attachment; filename={image_data['filename']}"}
    )


@router.delete("/images/{file_id}", response_model=dict)
async def delete_image(
    file_id: str,
    current_user: User = Depends(get_current_user),
    image_service: ImageService = Depends()
):
    success = await image_service.delete_image(file_id, current_user.id)
    if success:
        return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")


@router.post("/documents/", response_model=dict)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends()
):
    content = await file.read()
    file_id = await document_service.upload_document(file.filename, content, description, current_user.id)
    return {"id": file_id, "message": "Document uploaded successfully"}


@router.get("/documents/", response_model=List[dict])
async def get_user_documents(
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends()
):
    return await document_service.get_user_documents(current_user.id)


@router.get("/documents/{file_id}")
async def download_document(
    file_id: str,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends()
):
    document_data = await document_service.get_document(file_id, current_user.id)
    return StreamingResponse(
        io.BytesIO(document_data["content"]),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={document_data['filename']}"}
    )


@router.delete("/documents/{file_id}", response_model=dict)
async def delete_document(
    file_id: str,
    current_user: User = Depends(get_current_user),
    document_service: DocumentService = Depends()
):
    success = await document_service.delete_document(file_id, current_user.id)
    if success:
        return {"message": "Document deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
