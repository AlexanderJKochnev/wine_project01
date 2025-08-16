# app/support/file/router.py
from fastapi import UploadFile, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config.database.db_async import get_db
from app.core.routers.base import BaseRouter
from app.support.file.model import File
from app.support.file.repository import FileRepository
from app.support.file.schemas import FileRead, FileCreate, FileUpdate
from app.support.file.service import SeaweedFSClient
import uuid

seaweed = SeaweedFSClient()


class FileRouter(BaseRouter):
    def __init__(self):
        super().__init__(
            model=File,
            repo=FileRepository,
            create_schema=FileCreate,
            update_schema=FileUpdate,
            read_schema=FileRead,
            prefix="/files",
            tags=["files"]
        )
        self.setup_routes()

        # Переопределяем методы
        self.router.add_api_route("", self.upload_file, methods=["POST"], response_model=FileRead)
        self.router.add_api_route("/{id}", self.get_file, methods=["GET"], response_model=None)
        self.router.add_api_route("/{id}", self.delete_file, methods=["DELETE"], response_model=dict)
        self.router.add_api_route("/{id}", self.update_file, methods=["PATCH"], response_model=FileRead)

    async def upload_file(self, file: UploadFile, session: AsyncSession = Depends(get_db)) -> FileRead:
        file_id = str(uuid.uuid4())
        try:
            # 1. Загружаем в SeaweedFS
            await seaweed.upload(file, file_id)

            # 2. Сохраняем метаданные
            file_data = FileCreate(
                filename=file.filename,
                content_type=file.content_type,
                size=await file.seek(0, 2) or 0,  # размер
                seaweedfs_id=file_id
            )
            repo = FileRepository(session)
            db_file = await repo.create(file_data)

            return FileRead.from_orm(db_file)
        except Exception as e:
            # Откатываем загрузку при ошибке
            try:
                await seaweed.delete(file_id)
            except Exception as e:
                print(f'delete failed. {e}')
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    async def get_file(self, id: int, session: AsyncSession = Depends(get_db)):
        repo = FileRepository(session)
        db_file = await repo.get_by_id(id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        content, content_type = await seaweed.download(db_file.seaweedfs_id)
        return Response(content=content, media_type=content_type, headers={
            "Content-Disposition": f'inline; filename="{db_file.filename}"'
        })

    async def update_file(self, id: int, file: UploadFile, session: AsyncSession = Depends(get_db)) -> FileRead:
        repo = FileRepository(session)
        db_file = await repo.get_by_id(id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        try:
            # Обновляем файл в SeaweedFS
            await seaweed.update(file, db_file.seaweedfs_id)
            # Обновляем метаданные
            file_update = FileUpdate(filename=file.filename)
            db_file = await repo.update(db_file, file_update)
            return FileRead.from_orm(db_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    async def delete_file(self, id: int, session: AsyncSession = Depends(get_db)) -> dict:
        repo = FileRepository(session)
        db_file = await repo.get_by_id(id)
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        # Удаляем из SeaweedFS
        await seaweed.delete(db_file.seaweedfs_id)
        # Удаляем из БД
        await repo.delete(db_file)
        return {"status": "deleted", "id": id}

    # Для совместимости с BaseRouter
    async def create(self, data: FileCreate, session: AsyncSession = Depends(get_db)) -> FileRead:
        return await super().create(data, session)

    async def update(self, id: int, data: FileUpdate, session: AsyncSession = Depends(get_db)) -> FileRead:
        return await super().update(id, data, session)


from starlette.responses import Response  # noqa F402
router = FileRouter().router
