# tests/test_user_in_db.
import pytest
from sqlalchemy import select
from app.auth.models import User
from app.auth.repository import UserRepository    

async def test_admin_user_exists_in_test_database(test_db_session, create_superuser, super_user):   
    """Тест проверяет, что суперпользователь 'admin' существует в тестовой базе данных""" 
    # Создаем репозиторий для работы с пользователями  
    # Ищем пользователя по username
    stmt = select(User).where(User.username == "admin")
    result = await test_db_session.execute(stmt)  
    admin_user = result.scalar_one_or_none() 

    # Проверяем, что пользователь найден
    assert admin_user is not None, "Superuser 'admin' should exist in test database" 
    # Проверяем поля пользователя  
    assert admin_user.username == "admin"    
    assert admin_user.email == "admin@example.com"
    assert admin_user.is_active is True 
    assert admin_user.is_superuser is True   
    assert admin_user.hashed_password is not None 
    assert len(admin_user.hashed_password) > 0    


async def test_user_authentication_works(test_db_session):  
    """Тест проверяет, что аутентификация пользователя работает корректно"""    
    # Создаем репозиторий для работы с пользователями  
    user_repo = UserRepository()   

    # Проверяем успешную аутентификацию 
    authenticated_user = await user_repo.authenticate("admin", "admin", test_db_session)  
    assert authenticated_user is not None, "Authentication should succeed with correct credentials" 
    assert authenticated_user.username == "admin" 

    # Проверяем неуспешную аутентификацию с неверным паролем
    failed_auth = await user_repo.authenticate("admin", "wrongpassword", test_db_session) 
    assert failed_auth is None, "Authentication should fail with incorrect password" 


async def test_create_user_in_database(test_db_session):    
    """Тест проверяет создание нового пользователя в базе данных"""   
    # Создаем репозиторий для работы с пользователями  
    user_repo = UserRepository()   

    # Подготавливаем данные для создания пользователя  
    user_data = {"username": "testuser", "email": "test@example.com", "password": "testpass123"}    

    # Создаем пользователя    
    try:  
       new_user = await user_repo.create(user_data, test_db_session)

       # Проверяем, что пользователь создан
       assert new_user is not None
       assert new_user.username == "testuser"
       assert new_user.email == "test@example.com"
        # Проверяем, что пользователь сохранен в базе данных
       stmt = select(User).where(User.username == "testuser")
       result = await test_db_session.execute(stmt)
       saved_user = result.scalar_one_or_none()
       assert saved_user is not None
       assert saved_user.username == "testuser"

    except Exception as e:    
        pytest.fail(f"Failed to create user: {e}")