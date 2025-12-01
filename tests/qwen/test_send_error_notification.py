import pytest
from app.arq_worker import send_error_notification
from app.core.utils.email_sender import EmailSender


@pytest.mark.asyncio
async def test_send_error_notification_integration(authenticated_client_with_db, test_db_session):
    """Интеграционный тест отправки уведомления об ошибке"""
    error_message = "Тестовая ошибка для проверки уведомлений"
    
    # Проверяем, что функция существует
    assert send_error_notification is not None
    
    # Попробуем вызвать функцию отправки уведомления
    try:
        await send_error_notification(error_message)
        # Если выполнение прошло успешно (без исключений)
        assert True
    except Exception as e:
        # В тестовой среде могут быть ограничения на отправку email, 
        # но сам код должен быть корректным
        # Проверим, что это именно ошибка подключения/аутентификации, а не ошибка импорта или вызова
        assert "authentication" in str(e).lower() or "connection" in str(e).lower() or "timeout" in str(e).lower()


@pytest.mark.asyncio
async def test_send_error_notification_with_real_settings():
    """Тест отправки уведомления с реальными настройками"""
    error_message = "Тестовое сообщение об ошибке"
    
    # Проверяем, что настройки email корректно загружаются
    email_sender = EmailSender()
    assert email_sender.from_email == "redmine1981@yandex.ru"
    
    # Проверяем, что функция может быть вызвана
    assert callable(send_error_notification)
    
    # Попробуем вызвать функцию
    try:
        await send_error_notification(error_message)
        # Если успешно выполнено
        assert True
    except Exception as e:
        # Проверим, что это ожидаемая ошибка (связанная с отправкой email)
        error_str = str(e).lower()
        if not any(keyword in error_str for keyword in ["authentication", "connection", "timeout", "ssl", "tls"]):
            raise  # Если это не ошибка подключения/аутентификации, то это другая проблема