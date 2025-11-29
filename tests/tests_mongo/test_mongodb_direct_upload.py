import pytest
from bson import ObjectId
from fastapi import status

from app.core.utils.common_utils import jprint
from app.mongodb.router import (fileprefix, prefix, directprefix,
                                subprefix)  # Импортируем префиксы для корректного URL

pytestmark = pytest.mark.asyncio

async def test_mongodb_direct_upload(authenticated_client_with_db,
                                     test_db_session, sample_image_paths):
    """
    Тестирует mongodb upload_image.
    """
    from app.mongodb.models import DirectUploadResponse
    client = authenticated_client_with_db
    # 1. Загружаем изображения из директории по умолчанию
    response = await client.post(f"{prefix}/{directprefix}")
    assert response.status_code == 200, response.text
    result = response.json()
    jprint(result)
    assert False