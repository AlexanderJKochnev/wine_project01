# app/mongodb/router.py
import io
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.auth.dependencies import get_current_user
from app.mongodb.config import get_mongo_db
from app.mongodb.models import DocumentCreate, FileResponse, ImageCreate
from app.mongodb.service import MongoDBService

router = APIRouter(prefix="/mongodb", tags=["mongodb"])


async def get_mongo_service(db: AsyncIOMotorDatabase):
    """Dependency для инъекции MongoDBService"""
    return MongoDBService(db)


@router.post("/images/", response_model=dict)
async def upload_image(file: UploadFile = File(...),
                       description: Optional[str] = Form(None),
                       current_user: dict = Depends(get_current_user),
                       db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    content = await file.read()
    if len(content) > 8 * 1024 * 1024:  # 8MB limit
        raise HTTPException(status_code=400, detail="File too large")

    image_data = ImageCreate(filename=file.filename, description=description, content=content)

    file_id = await service.create_image(image_data, current_user["id"], db)
    return {"id": file_id, "message": "Image uploaded successfully"}


@router.get("/images/", response_model=List[FileResponse])
async def get_user_images(current_user: dict = Depends(get_current_user),
                          db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    return await service.get_user_images_list(current_user["id"])


@router.get("/images/{file_id}")
async def download_image(file_id: str,
                         current_user: dict = Depends(get_current_user),
                         db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    image_data = await service.get_image(file_id, current_user["id"])

    return StreamingResponse(io.BytesIO(image_data["content"]),
                             media_type="image/jpeg",
                             headers={"Content-Disposition": f"attachment; filename={image_data['filename']}"})


@router.delete("/images/{file_id}", response_model=dict)
async def delete_image(file_id: str,
                       current_user: dict = Depends(get_current_user),
                       db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    success = await service.delete_image(file_id, current_user["id"])
    if success:
        return {"message": "Image deleted successfully"}
    raise HTTPException(status_code=404, detail="Image not found")


# Аналогичные эндпоинты для документов
@router.post("/documents/", response_model=dict)
async def upload_document(file: UploadFile = File(...),
                          description: Optional[str] = Form(None),
                          current_user: dict = Depends(get_current_user),
                          db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    content = await file.read()
    if len(content) > 8 * 1024 * 1024:  # 8MB limit
        raise HTTPException(status_code=400, detail="File too large")

    doc_data = DocumentCreate(filename=file.filename,
                              description=description,
                              content=content)

    file_id = await service.create_document(doc_data, current_user["id"])
    return {"id": file_id, "message": "Document uploaded successfully"}


@router.get("/documents/", response_model=List[FileResponse])
async def get_user_documents(current_user: dict = Depends(get_current_user),
                             db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    return await service.get_user_documents_list(current_user["id"])


@router.get("/documents/{file_id}")
async def download_document(file_id: str,
                            current_user: dict = Depends(get_current_user),
                            db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    doc_data = await service.get_document(file_id, current_user["id"])

    return StreamingResponse(io.BytesIO(doc_data["content"]),
                             media_type="application/octet-stream",
                             headers={"Content-Disposition": f"attachment; filename={doc_data['filename']}"})


@router.delete("/documents/{file_id}", response_model=dict)
async def delete_document(file_id: str,
                          current_user: dict = Depends(get_current_user),
                          db: AsyncIOMotorDatabase = Depends(get_mongo_db)):
    service = get_mongo_service(db)
    success = await service.delete_document(file_id, current_user["id"])
    if success:
        return {"message": "Document deleted successfully"}
    raise HTTPException(status_code=404, detail="Document not found")
