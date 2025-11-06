# app/mongodb/debug_service_fixed.py
import asyncio
import motor.motor_asyncio
from app.mongodb.service import ThumbnailImageService
from app.mongodb.repository import ThumbnailImageRepository
from app.mongodb.config import settings


async def debug_service_fixed():
    """Проверка работы сервиса - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url, serverSelectionTimeoutMS = 5000)
    db = client[settings.MONGO_DATABASE]
    repository = ThumbnailImageRepository(db)
    service = ThumbnailImageService(repository)
    
    print("=== SERVICE DIAGNOSTIC FIXED ===")
    
    # Найдем тестовое изображение
    test_doc = await repository.collection.find_one({"has_thumbnail": True})
    if test_doc:
        file_id = str(test_doc['_id'])
        print(f"Testing with file: {test_doc['filename']} (ID: {file_id})")
        
        try:
            # Получаем thumbnail через сервис
            print("\n1. Getting thumbnail via service...")
            thumbnail_data = await service.get_thumbnail(file_id)
            if thumbnail_data and "content" in thumbnail_data:
                print(f"✅ Thumbnail from service: {len(thumbnail_data['content'])} bytes")
                print(f"Filename: {thumbnail_data['filename']}")
                print(f"From cache: {thumbnail_data.get('from_cache', False)}")
            else:
                print("❌ Thumbnail data is None or missing content")
                return
            
            # Получаем полное изображение
            print("\n2. Getting full image via service...")
            full_data = await service.get_full_image(file_id)
            if full_data and "content" in full_data:
                print(f"✅ Full image from service: {len(full_data['content'])} bytes")
                print(f"Filename: {full_data['filename']}")
            else:
                print("❌ Full image data is None or missing content")
                return
            
            # Сравниваем
            ratio = len(thumbnail_data['content']) / len(full_data['content']) * 100
            print(f"\n3. Size comparison:")
            print(f"Thumbnail: {len(thumbnail_data['content'])} bytes")
            print(f"Full image: {len(full_data['content'])} bytes")
            print(f"Ratio: {ratio:.1f}%")
            
            if ratio > 50:
                print("❌ PROBLEM: Thumbnail is too large!")
            else:
                print("✅ Thumbnail size looks good")
        
        except Exception as e:
            print(f"❌ Error during service test: {e}")
            import traceback
            traceback.print_exc()
    
    else:
        print("❌ No test documents found")
    
    client.close()


if __name__ == "__main__":
    asyncio.run(debug_service_fixed())