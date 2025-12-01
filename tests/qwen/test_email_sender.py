import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.utils.email_sender import EmailSender


@pytest.mark.asyncio
async def test_send_email_success():
    """Тест успешной отправки электронного письма"""
    email_sender = EmailSender()
    
    # Мок SMTP сервера
    with patch("app.core.utils.email_sender.smtplib.SMTP") as mock_smtp:
        mock_server_instance = AsyncMock()
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        # Вызов тестируемого метода
        await email_sender.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            body="Test Body"
        )
        
        # Проверки
        mock_smtp.assert_called_once_with(email_sender.smtp_host, email_sender.smtp_port)
        mock_server_instance.starttls.assert_called_once()
        mock_server_instance.login.assert_called_once_with(email_sender.username, email_sender.password)
        mock_server_instance.sendmail.assert_called_once()
        mock_server_instance.quit.assert_called_once()


@pytest.mark.asyncio
async def test_send_email_failure():
    """Тест неудачной отправки электронного письма"""
    email_sender = EmailSender()
    
    # Мок SMTP сервера с выбрасыванием исключения
    with patch("app.core.utils.email_sender.smtplib.SMTP") as mock_smtp:
        mock_server_instance = AsyncMock()
        mock_server_instance.login.side_effect = Exception("Login failed")
        mock_smtp.return_value.__enter__.return_value = mock_server_instance
        
        # Проверяем, что исключение передается дальше
        with pytest.raises(Exception, match="Login failed"):
            await email_sender.send_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                body="Test Body"
            )