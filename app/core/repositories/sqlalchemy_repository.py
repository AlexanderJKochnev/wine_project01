# app/core/repositories/sqlalchemy_repository.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, Dict, Optional, TypeVar, Generic
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy import select
from app.core.config.database.db_async import get_db
from app.core.utils.image_utils import ImageService

ModelType = TypeVar("ModelType", bound=DeclarativeMeta)


class Repository(Generic[ModelType]):
    model: ModelType

    def get_query(self):
        """
        Переопределяемый метод.
        Возвращает select() с нужными selectinload.
        По умолчанию — без связей.
        """
        return select(self.model)

    async def create(self, data: Dict[str, Any], session: AsyncSession = Depends(get_db)) -> ModelType:
        """ create & return record """
        # Обрабатываем изображение если модель поддерживает его
        if hasattr(self.model, 'image_path') and 'image_file' in data:
            image_file = data.pop('image_file')
            if image_file and hasattr(image_file, 'filename'):
                image_path = await ImageService.process_and_save_image(image_file)
                data['image_path'] = image_path

        obj = self.model(**data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def get_by_id(self, id: Any, session: AsyncSession = Depends(get_db)) -> Optional[ModelType]:
        """
        get one record by id
        """
        stmt = self.get_query().where(self.model.id == id)
        result = await session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj

    async def get_all(self, skip, limit, session: AsyncSession, ) -> dict:
        # Запрос с загрузкой связей и пагинацией
        stmt = self.get_query().offset(skip).limit(limit)
        result = await session.execute(stmt)
        items = result.scalars().all()
        return items

    async def update(self, id: Any, data: Dict[str, Any], session: AsyncSession) -> Optional[ModelType]:
        obj = await self.get_by_id(id, session)
        if not obj:
            return None

        # Обрабатываем изображение если модель поддерживает его
        if hasattr(self.model, 'image_path') and 'image_file' in data:
            image_file = data.pop('image_file')
            if image_file and hasattr(image_file, 'filename'):
                # Удаляем старое изображение если оно было
                if hasattr(obj, 'image_path') and obj.image_path:
                    ImageService.delete_image(obj.image_path)

                # Сохраняем новое изображение
                image_path = await ImageService.process_and_save_image(image_file)
                data['image_path'] = image_path
            elif image_file is None:
                # Явно удаляем изображение
                if hasattr(obj, 'image_path') and obj.image_path:
                    ImageService.delete_image(obj.image_path)
                data['image_path'] = None

        for k, v in data.items():
            if hasattr(obj, k):
                setattr(obj, k, v)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def delete(self, id: Any, session: AsyncSession) -> bool:
        obj = await self.get_by_id(id, session)
        if not obj:
            return False

        # Удаляем изображение если оно есть
        if hasattr(obj, 'image_path') and obj.image_path:
            ImageService.delete_image(obj.image_path)

        await session.delete(obj)
        await session.commit()
        return True

    async def get_by_field(self, field_name: str, field_value: Any, session: AsyncSession):
        stmt = select(self.model).where(getattr(self.model, field_name) == field_value)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
