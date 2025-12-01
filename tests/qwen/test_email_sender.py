import pytest
from unittest.mock import AsyncMock, patch
from app.core.utils.email_sender import EmailSender
from app.core.config.project_config import settings


@pytest.mark.asyncio
async def test_send_email_success():
    """Тест успешной отправки электронного письма"""
    email_sender = EmailSender()
    
    # Проверяем, что настройки загружаются корректно
    assert email_sender.smtp_host == settings.EMAIL_HOST
    assert email_sender.smtp_port == settings.EMAIL_PORT
    assert email_sender.username == settings.EMAIL_USERNAME
    assert email_sender.password == settings.EMAIL_PASSWORD
    assert email_sender.from_email == settings.EMAIL_FROM
    
    # Mock the SMTP connection to avoid actual email sending
    with patch('aiosmtplib.send') as mock_send:
        mock_send.return_value = AsyncMock()
        
        # Test sending an email
        await email_sender.send_email(
            to_email="test@example.com",
            subject="Тестовое уведомление",
            body="Тестовое сообщение для проверки работы email-уведомлений"
        )
        
        # Verify that aiosmtplib.send was called
        assert mock_send.called


@pytest.mark.asyncio
async def test_email_sender_configuration():
    """Тест конфигурации EmailSender с реальными настройками"""
    email_sender = EmailSender()
    
    # Проверяем, что настройки загружаются из конфигурации
    assert email_sender.smtp_host == settings.EMAIL_HOST
    assert email_sender.smtp_port == settings.EMAIL_PORT
    assert email_sender.username == settings.EMAIL_USERNAME
    assert email_sender.password == settings.EMAIL_PASSWORD
    assert email_sender.from_email == settings.EMAIL_FROM
    assert email_sender.use_ssl == settings.EMAIL_USE_SSL
    assert email_sender.use_tls == settings.EMAIL_USE_TLS