# app/support/seaweed/repository.py

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.support.seaweed.model import File
from app.support.seaweed.schemas import FileCreate


class FileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_file(self, file_data: FileCreate, seaweedfs_id: str) -> File:
        file = File(filename=file_data.filename,
                    content_type=file_data.content_type,
                    seaweedfs_id=seaweedfs_id,
                    size=file_data.size)
        self.session.add(file)
        await self.session.commit()
        await self.session.refresh(file)
        return file

    async def get_file(self, file_id: int) -> File | None:
        result = await self.session.execute(select(File).where(File.id == file_id))
        return result.scalar_one_or_none()
