# tests/mock/repository_mock.py
from typing import Any, Dict, Optional, List
from app.core.repositories.sqlalchemy_repository import Repository
# import asyncio


class MockRepository(Repository):
    """Mock репозиторий для тестирования"""

    def __init__(self):
        self._storage = {}
        self._id_counter = 1

    async def create(self, data: Dict[str, Any], session=None) -> Any:
        """Создание записи"""
        # Создаем объект модели с mock данными
        obj_data = {**data, "id": self._id_counter}
        self._storage[self._id_counter] = obj_data
        self._id_counter += 1
        return self._create_mock_object(obj_data)

    async def get_by_id(self, id: int, session=None) -> Optional[Any]:
        """Получение записи по ID"""
        data = self._storage.get(id)
        if data:
            return self._create_mock_object(data)
        return None

    async def get_all(self, skip: int, limit: int, session=None) -> List[Any]:
        """Получение всех записей с пагинацией"""
        all_items = list(self._storage.values())
        paginated = all_items[skip:skip + limit]
        return [self._create_mock_object(item) for item in paginated]

    async def update(self, id: int, data: Dict[str, Any], session=None) -> Optional[Any]:
        """Обновление записи"""
        if id in self._storage:
            self._storage[id].update(data)
            return self._create_mock_object(self._storage[id])
        return None

    async def delete(self, id: int, session=None) -> bool:
        """Удаление записи"""
        if id in self._storage:
            del self._storage[id]
            return True
        return False

    async def get_by_field(self, field_name: str, field_value: Any, session=None):
        """Получение записи по полю"""
        for item in self._storage.values():
            if item.get(field_name) == field_value:
                return self._create_mock_object(item)
        return None

    async def get_count(self, session=None) -> int:
        """Получение количества записей"""
        return len(self._storage)

    def _create_mock_object(self, data: Dict[str, Any]) -> Any:
        """Создание mock объекта"""

        class MockObject:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)

            def __getitem__(self, key):
                return getattr(self, key, None)

        return MockObject(**data)

    def add_mock_data(self, data: Dict[str, Any]) -> int:
        """Добавление тестовых данных"""
        obj_id = data.get("id", self._id_counter)
        if "id" not in data:
            data["id"] = obj_id
        self._storage[obj_id] = data
        if obj_id >= self._id_counter:
            self._id_counter = obj_id + 1
        return obj_id
