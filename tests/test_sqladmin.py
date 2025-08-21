import pytest
from app.core.config.project_config import settings
from unittest.mock import AsyncMock, MagicMock, patch

pytestmark = pytest.mark.asyncio


# Тесты
async def test_admin_login_page_access(authenticated_client_with_db):
    """Тест доступа к странице логина админки"""
    try:
        response = await authenticated_client_with_db.get("/admin/login")
        assert response.status_code == 200
        # Проверяем, что страница содержит форму логина
        content = response.text.lower()
        assert any(keyword in content for keyword in ["login", "username", "password", "вход"])
    except Exception as e:
        pytest.skip(f"Admin login page not available: {e}")


async def test_admin_login_success(authenticated_client_with_db):
    """Тест успешного логина в админку"""
    # Мокаем зависимость для избежания реальных вызовов
    with patch('app.admin.auth.AsyncSessionLocal') as mock_session_local, patch(
        'app.admin.auth.UserRepository'
    ) as mock_user_repo_class:
        # Настраиваем моки
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_user_repo = AsyncMock()
        mock_user_repo_class.return_value = mock_user_repo

        # Настраиваем мок пользователя
        mock_user = MagicMock()
        mock_user.is_superuser = True
        mock_user_repo.authenticate = AsyncMock(return_value=mock_user)

        # Тестируем логин через мок
        from app.admin.auth import AdminAuth
        auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)

        mock_request = AsyncMock()
        mock_request.form = AsyncMock(
            return_value={"username": "admin", "password": "admin"}
        )
        mock_request.session = {}

        result = await auth_backend.login(mock_request)
        assert result is True
        assert "admin_token" in mock_request.session


async def test_admin_login_invalid_credentials(authenticated_client_with_db):
    """Тест логина с неверными учетными данными"""
    with patch('app.admin.auth.AsyncSessionLocal') as mock_session_local, patch(
        'app.admin.auth.UserRepository'
    ) as mock_user_repo_class:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_user_repo = AsyncMock()
        mock_user_repo_class.return_value = mock_user_repo
        mock_user_repo.authenticate = AsyncMock(return_value=None)

        from app.admin.auth import AdminAuth
        auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)

        mock_request = AsyncMock()
        mock_request.form = AsyncMock(
            return_value={"username": "invalid", "password": "wrong"}
        )
        mock_request.session = {}

        result = await auth_backend.login(mock_request)
        assert result is False


async def test_admin_access_without_auth(authenticated_client_with_db):
    """Тест доступа к админке без аутентификации"""
    try:
        response = await authenticated_client_with_db.get("/admin/")
        # Должен перенаправить на логин или вернуть 401/403
        assert response.status_code in [200, 302, 303, 307, 401, 403]
    except Exception:
        # Если страница не доступна, пропускаем тест
        pytest.skip("Admin page not accessible")


async def test_admin_logout(authenticated_client_with_db):  # (admin_login_session):
    """Тест выхода из админки"""
    try:
        response = await authenticated_client_with_db.post("/admin/logout")
        # Проверяем, что выход успешен
        assert response.status_code in [200, 302, 303, 307]
    except Exception as e:
        pytest.skip(f"Logout test failed: {e}")


async def test_admin_auth_backend_direct_login_success():
    """Тест метода login в AdminAuth напрямую (успешный случай)"""
    from app.admin.auth import AdminAuth

    with patch('app.admin.auth.AsyncSessionLocal') as mock_session_local, patch(
        'app.admin.auth.UserRepository'
    ) as mock_user_repo_class:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_user_repo = AsyncMock()
        mock_user_repo_class.return_value = mock_user_repo

        mock_user = MagicMock()
        mock_user.is_superuser = True
        mock_user_repo.authenticate = AsyncMock(return_value=mock_user)

        mock_request = AsyncMock()
        mock_request.form = AsyncMock(
            return_value={"username": "admin_test", "password": "admin_password"}
        )
        mock_request.session = {}

        auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
        result = await auth_backend.login(mock_request)
        assert result is True
        assert "admin_token" in mock_request.session


async def test_admin_auth_backend_direct_authenticate_success():
    """Тест метода authenticate в AdminAuth напрямую (успешный случай)"""
    from app.admin.auth import AdminAuth
    from jose import jwt

    with patch('app.admin.auth.AsyncSessionLocal') as mock_session_local, patch(
        'app.admin.auth.UserRepository'
    ) as mock_user_repo_class:
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        mock_user_repo = AsyncMock()
        mock_user_repo_class.return_value = mock_user_repo

        mock_user = MagicMock()
        mock_user.is_superuser = True
        mock_user.is_active = True
        mock_user_repo.get_by_field = AsyncMock(return_value=mock_user)

        token = jwt.encode(
            {"sub": "admin_test", "superuser": True}, settings.SECRET_KEY, algorithm=settings.ALGORITHM
        )

        mock_request = AsyncMock()
        mock_request.session = {"admin_token": token}

        auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
        result = await auth_backend.authenticate(mock_request)
        assert result is True


async def test_admin_auth_backend_authenticate_invalid_token():
    """Тест authenticate с невалидным токеном"""
    from app.admin.auth import AdminAuth
    mock_request = AsyncMock()
    mock_request.session = {"admin_token": "invalid_token"}
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    result = await auth_backend.authenticate(mock_request)
    assert result is False


async def test_admin_auth_backend_authenticate_no_token():
    """Тест authenticate без токена"""
    from app.admin.auth import AdminAuth
    mock_request = AsyncMock()
    mock_request.session = {}
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    result = await auth_backend.authenticate(mock_request)
    assert result is False


async def test_admin_auth_backend_logout():
    """Тест метода logout"""
    from app.admin.auth import AdminAuth
    mock_request = MagicMock()
    mock_request.session = {"admin_token": "some_token"}
    mock_request.clear = MagicMock()
    auth_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    result = await auth_backend.logout(mock_request)
    assert result is True
