# app/mongodb/debug_migration.py
import asyncio
import motor.motor_asyncio
from app.mongodb.config import settings
from app.mongodb.repository import ThumbnailImageRepository
from PIL import Image
import io


async def debug_migration():
    """Диагностика проблемы с thumbnail'ами"""
    client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGO_DATABASE]
    repository = ThumbnailImageRepository(db)

    print("=== DIAGNOSTIC START ===")

    # 1. Проверим метод создания thumbnail
    print("\n1. Testing thumbnail creation...")
    test_image = await repository.collection.find_one({})
    if test_image and "content" in test_image:
        original_size = len(test_image["content"])
        print(f"Original image size: {original_size} bytes")

        thumbnail_content = repository._create_thumbnail_png(test_image["content"])
        if thumbnail_content:
            thumbnail_size = len(thumbnail_content)
            print(f"Thumbnail size: {thumbnail_size} bytes")
            print(f"Reduction: {thumbnail_size / original_size * 100:.1f}%")

            # Проверим размеры изображения
            original_img = Image.open(io.BytesIO(test_image["content"]))
            thumb_img = Image.open(io.BytesIO(thumbnail_content))
            print(f"Original dimensions: {original_img.size}")
            print(f"Thumbnail dimensions: {thumb_img.size}")
        else:
            print("❌ Thumbnail creation failed!")

    # 2. Проверим данные в базе
    print("\n2. Checking database data...")
    images_with_thumb = await repository.collection.count_documents({"has_thumbnail": True})
    images_total = await repository.collection.count_documents({})
    print(f"Images with thumbnails: {images_with_thumb}/{images_total}")

    # 3. Проверим конкретные документы
    print("\n3. Sample documents analysis:")
    sample_docs = await repository.collection.find({"has_thumbnail": True}).limit(3).to_list(3)
    for doc in sample_docs:
        print(f"Document {doc['_id']}:")
        print(f"  - filename: {doc['filename']}")
        print(f"  - size: {doc.get('size', 'N/A')}")
        print(f"  - thumbnail_size: {doc.get('thumbnail_size', 'N/A')}")
        if 'content' in doc and 'thumbnail' in doc:
            content_len = len(doc['content'])
            thumb_len = len(doc['thumbnail'])
            print(f"  - content length: {content_len}")
            print(f"  - thumbnail length: {thumb_len}")
            print(f"  - ratio: {thumb_len / content_len * 100:.1f}%")

    client.close()
    print("=== DIAGNOSTIC END ===")


if __name__ == "__main__":
    asyncio.run(debug_migration())
