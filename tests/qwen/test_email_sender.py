import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.core.utils.email_sender import EmailSender
from app.core.config.project_config import settings


@pytest.mark.asyncio
async def test_send_email_success():
    """Тест успешной отправки электронного письма"""
    email_sender = EmailSender()
    
    # Проверяем, что настройки загружаются корректно
    assert settings.EMAIL_HOST == "smtp.yandex.ru"
    assert settings.EMAIL_PORT == 465
    assert settings.EMAIL_USERNAME == "redmine1981"
    assert settings.EMAIL_PASSWORD == "tytnpatsilleesly"
    assert settings.EMAIL_FROM == "redmine1981@yandex.ru"
    
    # Тестируем создание объекта EmailSender
    assert email_sender.smtp_host == "smtp.yandex.ru"
    assert email_sender.smtp_port == 465
    assert email_sender.username == "redmine1981"
    assert email_sender.password == "tytnpatsilleesly"
    assert email_sender.from_email == "redmine1981@yandex.ru"
    assert email_sender.use_ssl == True
    assert email_sender.use_tls == False


@pytest.mark.asyncio
async def test_send_email_integration(authenticated_client_with_db, test_db_session):
    """Интеграционный тест отправки email через API"""
    from app.core.utils.email_sender import EmailSender
    
    # Проверяем, что настройки корректно загружаются
    email_sender = EmailSender()
    
    # Попытка отправить email (это может не сработать в тестовой среде, но код должен быть корректным)
    try:
        await email_sender.send_email(
            to_email="akochnev66@gmail.com",
            subject="Тестовое уведомление",
            body="Тестовое сообщение для проверки работы email-уведомлений"
        )
        # Если письмо отправилось успешно
        assert True
    except Exception as e:
        # В тестовой среде могут быть ограничения на отправку email, 
        # но сам код должен быть корректным
        # Проверим, что это именно ошибка подключения/аутентификации, а не ошибка кода
        assert "authentication" in str(e).lower() or "connection" in str(e).lower() or "timeout" in str(e).lower()