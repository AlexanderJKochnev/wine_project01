# tests/test_mock_db.py
import pytest
from fastapi import status
from sqlalchemy import select
from app.support.color.model import Color

pytestmark = pytest.mark.asyncio

async def test_get_colors_empty_db(authenticated_client_with_db):
    """Тест получения цветов из пустой базы данных"""
    response = await authenticated_client_with_db.get("/colors/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_create_and_get_color(authenticated_client_with_db, test_db_session):
    """Тест создания и получения цвета"""
    # Создаем цвет
    color_data = {"name": "Red", "name_ru": "Красный"}
    
    response = await authenticated_client_with_db.post("/colors/", json = color_data)
    assert response.status_code == 201  # или 200
    
    created_color = response.json()
    assert created_color["name"] == "Red"
    assert created_color["name_ru"] == "Красный"
    assert "id" in created_color
    
    # Получаем цвет по ID
    color_id = created_color["id"]
    response = await authenticated_client_with_db.get(f"/colors/{color_id}/")
    assert response.status_code == 200
    
    retrieved_color = response.json()
    assert retrieved_color["name"] == "Red"
    assert retrieved_color["id"] == color_id


async def test_get_all_colors_pagination(authenticated_client_with_db, test_db_session):
    """Тест пагинации при получении всех цветов"""
    
    # Создаем несколько цветов
    colors_data = [{"name": f"Color{i}", "name_ru": f"Цвет{i}"} for i in range(1, 6)]
    
    for color_data in colors_data:
        response = await authenticated_client_with_db.post("/colors/", json = color_data)
        assert response.status_code in [200, 201]
    
    # Получаем первую страницу
    response = await authenticated_client_with_db.get("/colors/?page=1&page_size=2")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["page"] == 1
    assert data["has_next"] == True


async def test_update_color(authenticated_client_with_db, test_db_session):
    """Тест обновления цвета"""
    
    # Создаем цвет
    color_data = {"name": "Blue", "name_ru": "Синий"}
    response = await authenticated_client_with_db.post("/colors/", json = color_data)
    assert response.status_code in [200, 201]
    
    color_id = response.json()["id"]
    
    # Обновляем цвет
    update_data = {"name": "Dark Blue", "name_ru": "Темно-синий"}
    response = await authenticated_client_with_db.patch(f"/colors/{color_id}/", json = update_data)
    assert response.status_code == 200
    
    updated_color = response.json()
    assert updated_color["name"] == "Dark Blue"
    assert updated_color["name_ru"] == "Темно-синий"


async def test_delete_color(authenticated_client_with_db, test_db_session):
    """Тест удаления цвета"""
    
    # Создаем цвет
    color_data = {"name": "Green", "name_ru": "Зеленый"}
    response = await authenticated_client_with_db.post("/colors/", json = color_data)
    assert response.status_code in [200, 201]
    
    color_id = response.json()["id"]
    
    # Удаляем цвет
    response = await authenticated_client_with_db.delete(f"/colors/{color_id}/")
    assert response.status_code == 204  # или 200
    
    # Проверяем, что цвет удален
    response = await authenticated_client_with_db.get(f"/colors/{color_id}/")
    assert response.status_code == 404
