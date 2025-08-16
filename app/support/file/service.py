# app/support/file/service.py

import httpx
from fastapi import HTTPException, UploadFile
from app.core.config.seaweed import setting_seaweed


class SeaweedFSClient:
    def __init__(self):
        self.base_url = setting_seaweed.filer_uploads_url

    async def upload(self, file: UploadFile, file_id: str) -> dict:
        content = await file.read()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{file_id}",
                content=content,
                headers={"Content-Type": file.content_type}
            )
        if response.status_code not in (200, 201):
            raise HTTPException(
                status_code=500,
                detail=f"SeaweedFS upload failed: {response.text}"
            )
        return response.json()

    async def download(self, file_id: str) -> tuple[bytes, str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/{file_id}")
            if response.status_code == 404:
                raise HTTPException(status_code=404, detail="File not found in SeaweedFS")
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail="Download failed")
            return response.content, response.headers.get("Content-Type", "application/octet-stream")

    async def delete(self, file_id: str) -> bool:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{self.base_url}/{file_id}")
            # Даже если 404 — файл уже удалён
            return response.status_code in (200, 204, 404)

    async def update(self, file: UploadFile, file_id: str) -> dict:
        # Просто перезаписываем файл по тому же ID
        return await self.upload(file, file_id)
