# app/mongodb/router.py
import io
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from app.auth.dependencies import get_current_user  # Из вашей аутентификации
from app.mongodb.models import DocumentResponse, ImageResponse
from app.mongodb.service import DocumentCreate, get_mongo_service, ImageCreate, MongoDBService

router = APIRouter(prefix="/mongodb", tags=["mongodb"])


@router.post("/images/", response_model=dict)
async def upload_image(file: UploadFile = File(...), description: Optional[str] = Form(None),
                       current_user: dict = Depends(get_current_user),
                       service: MongoDBService = Depends(get_mongo_service)):
    content = await file.read()
    image_data = {"filename": file.filename, "description": description, "content": content}

    file_id = await service.create_image(ImageCreate(**image_data), current_user["id"])
    return {"id": file_id, "message": "Image uploaded successfully"}


@router.get("/images/", response_model=List[ImageResponse])
async def get_user_images(current_user: dict = Depends(get_current_user),
                          service: MongoDBService = Depends(get_mongo_service)):
    return await service.get_user_images_list(current_user["id"])


@router.get("/images/{file_id}")
async def download_image(file_id: str,
                         current_user: dict = Depends(get_current_user),
                         service: MongoDBService = Depends(get_mongo_service)):

    image_data = await service.get_image(file_id, current_user["id"])

    return StreamingResponse(io.BytesIO(image_data["content"]), media_type="image/jpeg",
                             headers={"Content-Disposition": f"attachment; filename={image_data['filename']}"})


@router.delete("/images/{file_id}", response_model=dict)
async def delete_image(file_id: str,
                       current_user: dict = Depends(get_current_user),
                       service: MongoDBService = Depends(get_mongo_service)):
    success = await service.delete_image(file_id, current_user["id"])
    if success:
        return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=404, detail="Image not found")


@router.post("/documents/", response_model=dict)
async def upload_document(file: UploadFile = File(...),
                          description: Optional[str] = Form(None),
                          current_user: dict = Depends(get_current_user),
                          service: MongoDBService = Depends(get_mongo_service)):
    content = await file.read()
    doc_data = {"filename": file.filename, "description": description, "content": content}

    file_id = await service.create_document(DocumentCreate(**doc_data), current_user["id"])
    return {"id": file_id, "message": "Document uploaded successfully"}


@router.get("/documents/", response_model=List[DocumentResponse])
async def get_user_documents(current_user: dict = Depends(get_current_user),
                             service: MongoDBService = Depends(get_mongo_service)):
    return await service.get_user_documents_list(current_user["id"])


@router.get("/documents/{file_id}")
async def download_document(file_id: str,
                            current_user: dict = Depends(get_current_user),
                            service: MongoDBService = Depends(get_mongo_service)):

    doc_data = await service.get_document(file_id, current_user["id"])

    return StreamingResponse(io.BytesIO(doc_data["content"]), media_type="application/octet-stream",
                             headers={"Content-Disposition": f"attachment; filename={doc_data['filename']}"})


@router.delete("/documents/{file_id}", response_model=dict)
async def delete_document(file_id: str, current_user: dict = Depends(get_current_user),
                          service: MongoDBService = Depends(get_mongo_service)):
    success = await service.delete_document(file_id, current_user["id"])
    if success:
        return {"message": "Document deleted successfully"}
    raise HTTPException(status_code=404, detail="Document not found")
