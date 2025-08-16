# app/support/file/repository.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Depends
from app.core.config.database.db_async import get_db
from app.support.file.model import File
from app.support.file.schemas import FileCreate, FileUpdate


class FileRepository:
    def __init__(self, session: AsyncSession = Depends(get_db)):
        self.session = session

    async def create(self, data: FileCreate) -> File:
        file = File(**data.dict())
        self.session.add(file)
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def get(self, file_id: str) -> File | None:
        result = await self.session.execute(select(File).where(File.seaweedfs_id == file_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, id: int) -> File | None:
        result = await self.session.execute(select(File).where(File.id == id))
        return result.scalar_one_or_none()

    async def update(self, db_file: File, data: FileUpdate) -> File:
        for k, v in data.dict(exclude_unset=True).items():
            setattr(db_file, k, v)
        await self.session.commit()
        await self.session.refresh(db_file)
        return db_file

    async def delete(self, db_file: File) -> bool:
        await self.session.delete(db_file)
        await self.session.commit()
        return True
