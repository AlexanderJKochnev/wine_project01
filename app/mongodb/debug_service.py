# app/mongodb/debug_sevice.py
import asyncio
import motor.motor_asyncio
from app.mongodb.service import ThumbnailImageService
from app.mongodb.repository import ThumbnailImageRepository
from app.mongodb.config import settings

async def debug_service():
    """Проверка работы сервиса"""
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGO_DATABASE]
    repository = ThumbnailImageRepository(db)
    service = ThumbnailImageService(repository)
    
    print("=== SERVICE DIAGNOSTIC ===")
    
    # Найдем тестовое изображение
    test_doc = await repository.collection.find_one({"has_thumbnail": True})
    if test_doc:
        file_id = str(test_doc['_id'])
        print(f"Testing with file: {test_doc['filename']} (ID: {file_id})")
        
        # Получаем thumbnail через сервис
        print("\nGetting thumbnail via service...")
        thumbnail_data = await service.get_thumbnail(file_id)
        print(f"Thumbnail from service: {len(thumbnail_data['content'])} bytes")
        print(f"Filename: {thumbnail_data['filename']}")
        print(f"From cache: {thumbnail_data.get('from_cache', False)}")
        
        # Получаем полное изображение
        print("\nGetting full image via service...")
        full_data = await service.get_full_image(file_id)
        print(f"Full image from service: {len(full_data['content'])} bytes")
        print(f"Filename: {full_data['filename']}")
        
        # Сравниваем
        ratio = len(thumbnail_data['content']) / len(full_data['content']) * 100
        print(f"\nSize ratio: {ratio:.1f}%")
        
        if ratio > 50:
            print("❌ PROBLEM: Thumbnail is too large!")
        else:
            print("✅ Thumbnail size looks good")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(debug_service())