import pytest
from unittest.mock import AsyncMock, patch
from app.arq_worker import send_error_notification


@pytest.mark.asyncio
async def test_send_error_notification():
    """Тест отправки уведомления об ошибке"""
    error_message = "Test error message"
    
    with patch("app.arq_worker.EmailSender") as mock_email_sender_class:
        # Мок экземпляра EmailSender
        mock_email_sender_instance = AsyncMock()
        mock_email_sender_class.return_value = mock_email_sender_instance
        
        # Вызов тестируемой функции
        await send_error_notification(error_message)
        
        # Проверки
        mock_email_sender_class.assert_called_once()
        mock_email_sender_instance.send_email.assert_called_once()
        
        # Проверяем аргументы вызова send_email
        args, kwargs = mock_email_sender_instance.send_email.call_args
        assert args[0] == "your_email@gmail.com"  # to_email (по умолчанию используется EMAIL_USERNAME)
        assert args[1] == "Ошибка воркера ARQ"  # subject
        assert error_message in args[2]  # body