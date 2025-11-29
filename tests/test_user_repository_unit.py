"""
Модульные тесты для UserRepository
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.auth.repository import UserRepository
from app.auth.models import User


@pytest.fixture
def mock_session():
    """Мок сессии базы данных"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.refresh = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Мок объекта пользователя"""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = "$2b$12$example_hashed_password"
    user.is_active = True
    user.is_superuser = False
    return user


@pytest.mark.asyncio
class TestUserRepository:
    
    async def test_verify_password_success(self):
        """Тест успешной проверки пароля"""
        # Подготовка
        plain_password = "testpassword"
        hashed_password = UserRepository.get_password_hash(plain_password)
        
        # Выполнение
        result = UserRepository.verify_password(plain_password, hashed_password)
        
        # Проверка
        assert result is True

    async def test_verify_password_failure(self):
        """Тест неудачной проверки пароля"""
        # Подготовка
        plain_password = "testpassword"
        wrong_password = "wrongpassword"
        hashed_password = UserRepository.get_password_hash(plain_password)
        
        # Выполнение
        result = UserRepository.verify_password(wrong_password, hashed_password)
        
        # Проверка
        assert result is False

    async def test_get_password_hash(self):
        """Тест хеширования пароля"""
        # Подготовка
        password = "testpassword"
        
        # Выполнение
        hashed = UserRepository.get_password_hash(password)
        
        # Проверка
        assert hashed != password
        assert "$2b$" in hashed  # bcrypt hash format

    async def test_authenticate_success(self, mock_session):
        """Тест успешной аутентификации пользователя"""
        # Подготовка
        username = "testuser"
        password = "testpassword"
        hashed_password = UserRepository.get_password_hash(password)
        
        # Создаем отдельный мок пользователя для этого теста
        mock_user = MagicMock(spec=User)
        mock_user.hashed_password = hashed_password
        
        # Мокируем выполнение запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Выполнение
        result = await UserRepository.authenticate(username, password, mock_session)
        
        # Проверка
        assert result == mock_user
        mock_session.execute.assert_called_once()

    async def test_authenticate_wrong_password(self, mock_session):
        """Тест аутентификации с неправильным паролем"""
        # Подготовка
        username = "testuser"
        password = "testpassword"
        wrong_password = "wrongpassword"
        hashed_password = UserRepository.get_password_hash(password)
        
        # Создаем отдельный мок пользователя для этого теста
        mock_user = MagicMock(spec=User)
        mock_user.hashed_password = hashed_password
        
        # Мокируем выполнение запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Выполнение
        result = await UserRepository.authenticate(username, wrong_password, mock_session)
        
        # Проверка
        assert result is None

    async def test_authenticate_user_not_found(self, mock_session):
        """Тест аутентификации несуществующего пользователя"""
        # Подготовка
        username = "nonexistent"
        password = "anypassword"
        
        # Мокируем выполнение запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)
        
        # Выполнение
        result = await UserRepository.authenticate(username, password, mock_session)
        
        # Проверка
        assert result is None

    async def test_create_user_success(self, mock_session):
        """Тест успешного создания пользователя"""
        # Подготовка
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "newpassword"
        }
        
        # Мокируем объект пользователя
        created_user = MagicMock()
        created_user.hashed_password = "hashed_password"
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Мокируем модель User
        with patch('app.auth.repository.User') as mock_user_class:
            mock_user_class.return_value = created_user
            # Выполнение
            result = await UserRepository.create(user_data, mock_session)
            
            # Проверка
            assert result is not None
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.refresh.assert_called_once()

    async def test_get_superuser_by_username_success(self, mock_session):
        """Тест получения суперпользователя по имени"""
        # Подготовка
        username = "admin"
        
        # Создаем отдельный мок пользователя для этого теста
        mock_user = MagicMock(spec=User)
        mock_user.is_superuser = True
        mock_user.is_active = True
        
        # Мокируем выполнение запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        execute_mock = AsyncMock(return_value=mock_result)
        mock_session.execute = execute_mock
        
        # Выполнение
        result = await UserRepository.get_superuser_by_username(username, mock_session)
        
        # Проверка
        assert result == mock_user
        execute_mock.assert_called_once()

    async def test_get_superuser_by_username_not_found(self, mock_session):
        """Тест получения несуществующего суперпользователя"""
        # Подготовка
        username = "nonexistent_admin"
        
        # Мокируем выполнение запроса
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        execute_mock = AsyncMock(return_value=mock_result)
        mock_session.execute = execute_mock
        
        # Выполнение
        result = await UserRepository.get_superuser_by_username(username, mock_session)
        
        # Проверка
        assert result is None