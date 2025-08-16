# app/support/drink/repository.py
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from app.core.repositories.sqlalchemy_repository import Repository
from app.support.drink.model import Drink
from app.support.region.model import Region
from app.core.utils.image_utils import ImageService


# DrinkRepository = RepositoryFactory.get_repository(Drink)
class DrinkRepository(Repository):
    model = Drink

    def get_query(self):
        # Добавляем загрузку связи с relationships
        """return select(Drink).options(selectinload(Drink.category)
                                     # selectinload(Drink.food),
                                     # selectinload(Drink.sweetness),
                                     # selectinload(Drink.color)
                                     )"""
        return select(Drink).options(joinedload(Drink.region)
                                     .joinedload(Region.country),
                                     joinedload(Drink.category),
                                     joinedload(Drink.food),
                                     joinedload(Drink.color),
                                     joinedload(Drink.sweetness),
                                     )

    async def create(self, data: dict, session):
        # Обрабатываем изображение если оно есть
        if 'image_file' in data:
            image_file = data.pop('image_file')
            if image_file and hasattr(image_file, 'filename'):
                image_path = await ImageService.process_and_save_image(image_file)
                data['image_path'] = image_path

        return await super().create(data, session)

    async def update(self, id: int, data: dict, session):
        # Получаем существующий объект
        existing_obj = await self.get_by_id(id, session)
        if not existing_obj:
            return None

        # Обрабатываем изображение если оно есть
        if 'image_file' in data:
            image_file = data.pop('image_file')
            if image_file and hasattr(image_file, 'filename'):
                # Удаляем старое изображение если оно было
                if existing_obj.image_path:
                    ImageService.delete_image(existing_obj.image_path)

                # Сохраняем новое изображение
                image_path = await ImageService.process_and_save_image(image_file)
                data['image_path'] = image_path
            elif image_file is None:
                # Явно удаляем изображение
                if existing_obj.image_path:
                    ImageService.delete_image(existing_obj.image_path)
                data['image_path'] = None

        return await super().update(id, data, session)

    async def delete(self, id: int, session) -> bool:
        # Получаем объект для удаления изображения
        obj = await self.get_by_id(id, session)
        if obj and obj.image_path:
            ImageService.delete_image(obj.image_path)
        return await super().delete(id, session)
