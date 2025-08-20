# tests/test_fastapi2.py
import pytest
from fastapi import status
from sqlalchemy import select
from app.support.color.model import Color


async def test_login(authenticated_client_with_db, test_db_session):
    response = await authenticated_client_with_db.post('/login/')
    assert response.status_code == 200


async def test_create_color_through_fastapi(authenticated_client_with_db, test_db_session):
    """Тест создания цвета через FastAPI endpoint"""
    # Подготавливаем данные для создания цвета
    color_data = {"name": "Red", "name_ru": "Красный", "description": "Красный цвет"}

    # Отправляем POST запрос через FastAPI
    response = await authenticated_client_with_db.post("/colors/", json=color_data, follow_redirects=True)

    # Проверяем успешный ответ
    assert response.status_code in [200, 201], f"Expected 200 or 201, got {response.status_code}"

    # Проверяем данные в ответе
    response_data = response.json()
    assert response_data["name"] == "Red"
    assert response_data["name_ru"] == "Красный"
    assert response_data["description"] == "Красный цвет"
    assert "id" in response_data
    assert isinstance(response_data["id"], int)
    # Проверяем, что запись действительно создана в базе данных
    color_id = response_data["id"]
    stmt = select(Color).where(Color.id == color_id)
    result = await test_db_session.execute(stmt)
    db_color = result.scalar_one_or_none()

    assert db_color is not None, "Color should be created in database"
    assert db_color.name == "Red"
    assert db_color.name_ru == "Красный"
    assert db_color.description == "Красный цвет"


async def test_create_color_and_verify_persistence(authenticated_client_with_db, test_db_session):
    """Тест создания цвета и проверки его сохранения в базе данных"""
    # Создаем цвет через API
    color_data = {"name": "Blue", "name_ru": "Синий"}

    create_response = await authenticated_client_with_db.post("/colors/", json = color_data)
    assert create_response.status_code in [200, 201]

    created_color = create_response.json()
    color_id = created_color["id"]

    # Получаем цвет через API по ID
    get_response = await authenticated_client_with_db.get(f"/colors/{color_id}/")
    assert get_response.status_code == 200

    retrieved_color = get_response.json()
    assert retrieved_color["name"] == "Blue"
    assert retrieved_color["name_ru"] == "Синий"
    assert retrieved_color["id"] == color_id
    
    # Проверяем через прямой запрос к базе данных
    stmt = select(Color).where(Color.id == color_id)
    result = await test_db_session.execute(stmt)
    db_color = result.scalar_one_or_none()
    
    assert db_color is not None
    assert db_color.name == "Blue"
    assert db_color.name_ru == "Синий"


async def test_create_multiple_colors_and_list_them(authenticated_client_with_db, test_db_session):
    """Тест создания нескольких цветов и получения списка"""
    # Создаем несколько цветов
    colors_data = [{"name": "Red", "name_ru": "Красный"}, {"name": "Green", "name_ru": "Зеленый"},
            {"name": "Blue", "name_ru": "Синий"}]
    
    created_colors = []
    for color_data in colors_data:
        response = await authenticated_client_with_db.post("/colors/", json = color_data)
        assert response.status_code in [200, 201]
        created_colors.append(response.json())
    
    # Получаем список всех цветов
    list_response = await authenticated_client_with_db.get("/colors/")
    assert list_response.status_code == 200
    
    list_data = list_response.json()
    assert "items" in list_data
    assert "total" in list_data
    assert list_data["total"] >= 3  # Может быть больше, если были другие тесты
    
    # Проверяем, что созданные цвета есть в списке
    response_colors = {color["name"]: color for color in list_data["items"]}
    for original_color in colors_data:
        assert original_color["name"] in response_colors
        assert response_colors[original_color["name"]]["name_ru"] == original_color["name_ru"]


async def test_create_color_with_minimal_data(authenticated_client_with_db, test_db_session):
    """Тест создания цвета с минимальными данными"""
    # Создаем цвет только с обязательными полями
    minimal_color_data = {"name": "Purple"# name_ru не обязателен
            }
    
    response = await authenticated_client_with_db.post("/colors/", json = minimal_color_data)
    assert response.status_code in [200, 201]
    
    created_color = response.json()
    assert created_color["name"] == "Purple"
    assert "id" in created_color
    
    # Проверяем в базе данных
    color_id = created_color["id"]
    stmt = select(Color).where(Color.id == color_id)
    result = await test_db_session.execute(stmt)
    db_color = result.scalar_one_or_none()
    
    assert db_color is not None
    assert db_color.name == "Purple"  # name_ru может быть None