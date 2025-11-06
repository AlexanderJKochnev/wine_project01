# app/mongodb/migration.py
import asyncio
from app.mongodb.repository import ThumbnailImageRepository
from app.mongodb.config import get_database


async def migrate_existing_images():
    """Миграция существующих изображений - добавление thumbnail'ов"""
    db = await get_database()
    repository = ThumbnailImageRepository(db)

    print("Starting image migration...")

    # Получаем все изображения без thumbnail'ов
    images = await repository.get_all_images_without_thumbnail()
    print(f"Found {len(images)} images without thumbnails")

    success_count = 0
    error_count = 0

    for image in images:
        try:
            print(f"Processing image: {image['filename']}")

            # Создаем thumbnail
            thumbnail_content = repository._create_thumbnail_png(image["content"])

            if thumbnail_content:
                # Обновляем документ
                updated = await repository.update_image_with_thumbnail(
                    image["_id"], thumbnail_content
                )

                if updated:
                    success_count += 1
                    print(f"✓ Added thumbnail for {image['filename']}")
                else:
                    error_count += 1
                    print(f"✗ Failed to update {image['filename']}")
            else:
                error_count += 1
                print(f"✗ Failed to create thumbnail for {image['filename']}")

        except Exception as e:
            error_count += 1
            print(f"✗ Error processing {image['filename']}: {e}")

    print(f"Migration completed: {success_count} successful, {error_count} errors")


if __name__ == "__main__":
    asyncio.run(migrate_existing_images())
