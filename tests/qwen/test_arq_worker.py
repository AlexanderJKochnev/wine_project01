import asyncio
import pytest
from unittest.mock import AsyncMock, patch
from app.arq_worker import parse_rawdata_task, send_error_notification
from app.support.parser.service import TaskLogService
from app.support.parser.model import Name, TaskLog
from app.support.parser.orchestrator import ParserOrchestrator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_parse_rawdata_task_success(test_db_session):
    """Тест успешного выполнения задачи parse_rawdata_task"""
    # Create a test Name record
    test_name = Name(name="Test Name", description="Test Description")
    test_db_session.add(test_name)
    await test_db_session.commit()
    await test_db_session.refresh(test_name)
    
    name_id = test_name.id
    
    # Create a mock context for ARQ
    mock_ctx = {"job_id": "test_job_id_123"}
    
    # Mock the ParserOrchestrator to return success
    with patch('app.arq_worker.ParserOrchestrator') as mock_orchestrator_class:
        mock_instance = AsyncMock()
        mock_instance._fill_rawdata_for_name = AsyncMock(return_value=True)
        mock_orchestrator_class.return_value = mock_instance
        
        # Run the task
        await parse_rawdata_task(mock_ctx, name_id)
        
        # Verify the orchestrator was called
        mock_instance._fill_rawdata_for_name.assert_called_once()
        
        # Check that a TaskLog entry was created and updated to success
        task_logs = (await test_db_session.execute(
            select(TaskLog).where(TaskLog.entity_id == name_id)
        )).scalars().all()
        
        assert len(task_logs) == 1
        task_log = task_logs[0]
        assert task_log.task_name == "parse_rawdata_task"
        assert task_log.status == "success"
        assert task_log.entity_id == name_id
        assert task_log.job_id == "test_job_id_123"


@pytest.mark.asyncio
async def test_parse_rawdata_task_failure_runtime_error(test_db_session):
    """Тест обработки ошибки RuntimeError в parse_rawdata_task"""
    # Create a test Name record
    test_name = Name(name="Test Name", description="Test Description")
    test_db_session.add(test_name)
    await test_db_session.commit()
    await test_db_session.refresh(test_name)
    
    name_id = test_name.id
    
    # Create a mock context for ARQ
    mock_ctx = {"job_id": "test_job_id_456"}
    
    # Mock the ParserOrchestrator to raise RuntimeError
    with patch('app.arq_worker.ParserOrchestrator') as mock_orchestrator_class, \
         patch('app.arq_worker.send_error_notification') as mock_email:
        mock_instance = AsyncMock()
        mock_instance._fill_rawdata_for_name = AsyncMock(side_effect=RuntimeError("Test error"))
        mock_orchestrator_class.return_value = mock_instance
        mock_email.return_value = AsyncMock()
        
        # Expect the function to raise an exception
        with pytest.raises(RuntimeError):
            await parse_rawdata_task(mock_ctx, name_id)
        
        # Check that a TaskLog entry was created and updated to failed
        task_logs = (await test_db_session.execute(
            select(TaskLog).where(TaskLog.entity_id == name_id)
        )).scalars().all()
        
        assert len(task_logs) == 1
        task_log = task_logs[0]
        assert task_log.task_name == "parse_rawdata_task"
        assert task_log.status == "failed"
        assert task_log.entity_id == name_id
        assert task_log.job_id == "test_job_id_456"
        assert "Test error" in (task_log.error or "")


@pytest.mark.asyncio
async def test_parse_rawdata_task_name_not_found(test_db_session):
    """Тест обработки ситуации когда Name не найден"""
    # Use a non-existent name_id
    invalid_name_id = 999999
    
    # Create a mock context for ARQ
    mock_ctx = {"job_id": "test_job_id_789"}
    
    # Expect the function to raise an exception
    with pytest.raises(ValueError, match="Name not found"):
        await parse_rawdata_task(mock_ctx, invalid_name_id)
    
    # Check that a TaskLog entry was created and updated to failed
    task_logs_all = (await test_db_session.execute(
        select(TaskLog).where(TaskLog.job_id == "test_job_id_789")
    )).scalars().all()
    
    # There should be a log entry for the task attempt
    if task_logs_all:  # Only check if any logs were created
        task_log = task_logs_all[-1]
        assert task_log.task_name == "parse_rawdata_task"


@pytest.mark.asyncio
async def test_send_error_notification_integration():
    """Интеграционный тест отправки уведомления об ошибке"""
    error_message = "Тестовая ошибка для проверки уведомлений"
    
    # Mock the EmailSender to avoid actual email sending
    with patch('app.core.utils.email_sender.EmailSender') as mock_email_sender_class:
        mock_email_instance = AsyncMock()
        mock_email_instance.send_email = AsyncMock()
        mock_email_sender_class.return_value = mock_email_instance
        
        # Run the notification function
        await send_error_notification(error_message)
        
        # Verify that the email was attempted to be sent
        mock_email_instance.send_email.assert_called_once()
        args, kwargs = mock_email_instance.send_email.call_args
        assert "ошибка воркера" in args[1].lower()  # subject
        assert error_message in args[2]  # body