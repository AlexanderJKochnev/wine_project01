# app/support/seaweed/router.py
from fastapi import APIRouter, UploadFile, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from botocore.exceptions import ClientError
from app.support.seaweed.repository import FileRepository
from app.core.config.database.db_noclass import get_db
from app.core.config.seaweed import get_s3_client
from app.support.seaweed.schemas import FileCreate, FileResponse


router = APIRouter(prefix="/files", tags=["files"])


async def ensure_bucket_exists(s3):
    try:
        await s3.head_bucket(Bucket="uploads")
    except Exception:
        await s3.create_bucket(Bucket="uploads")


@router.post("/upload", response_model=FileResponse)
async def upload_file(file: UploadFile,
                      db: AsyncSession = Depends(get_db),
                      s3_client=Depends(get_s3_client)):
    file_id = str(uuid.uuid4())
    file_content = await file.read()
    async with s3_client as client:
        try:
            await client.head_bucket(Bucket="uploads")
        except ClientError:
            print('Bucket "uploads" does not exist, create "uploads" directory thru web interface..')
        await client.put_object(
            Bucket="uploads",
            Key=file_id,
            Body=file_content,
            ContentType=file.content_type,
        )

    repo = FileRepository(db)
    file_data = FileCreate(filename=file.filename,
                           content_type=file.content_type,
                           size=len(file_content))

    db_file = await repo.create_file(file_data, file_id)
    return {"id": db_file.id,
            "filename": db_file.filename,
            "content_type": db_file.content_type,
            "size": db_file.size,
            "seaweedfs_id": db_file.seaweedfs_id}


@router.get("/download/{file_id}")
async def download_file(file_id: int,
                        db: AsyncSession = Depends(get_db),
                        s3=Depends(get_s3_client)):
    repo = FileRepository(db)
    file = await repo.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        async with s3 as client:
            response = await client.get_object(Bucket="uploads",
                                               Key=file.seaweedfs_id)
            content = await response["Body"].read()

        return StreamingResponse(iter([content]),
                                 media_type=file.content_type,
                                 headers={"Content-Disposition": f"attachment; "
                                                                 f"filename={file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"File download failed: {str(e)}")
