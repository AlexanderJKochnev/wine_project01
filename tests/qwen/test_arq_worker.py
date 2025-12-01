import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.arq_worker import parse_rawdata_task
from app.support.parser.service import TaskLogService
from app.support.parser.model import Name
from app.support.parser.orchestrator import ParserOrchestrator
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_parse_rawdata_task_success():
    """Тест успешного выполнения задачи parse_rawdata_task"""
    # Подготовка моков
    mock_ctx = {"job_id": "test_job_id"}
    mock_name_id = 1
    mock_task_log_id = 123

    with patch.object(TaskLogService, "add", return_value=mock_task_log_id) as mock_add, \
         patch.object(TaskLogService, "update", return_value=None) as mock_update, \
         patch("app.arq_worker.AsyncSessionLocal") as mock_session_local, \
         patch("app.arq_worker.smooth_delay", return_value=None), \
         patch("app.arq_worker.get_db") as mock_get_db:

        # Мок сессии
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_session

        # Мок объекта Name
        mock_name = MagicMock(spec=Name)
        mock_session.get.return_value = mock_name

        # Мок оркестратора
        mock_orchestrator = AsyncMock(spec=ParserOrchestrator)
        mock_orchestrator._fill_rawdata_for_name.return_value = True

        with patch("app.arq_worker.ParserOrchestrator", return_value=mock_orchestrator):
            # Вызов тестируемой функции
            await parse_rawdata_task(mock_ctx, mock_name_id)

            # Проверки
            mock_add.assert_called_once_with(
                task_name="parse_rawdata_task",
                job_id="test_job_id",
                name_id=mock_name_id,
                session=mock_get_db
            )
            mock_update.assert_called_once_with(
                mock_task_log_id,
                'success',
                None,
                session=mock_get_db
            )
            mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_parse_rawdata_task_failure():
    """Тест неудачного выполнения задачи parse_rawdata_task"""
    # Подготовка моков
    mock_ctx = {"job_id": "test_job_id"}
    mock_name_id = 1
    mock_task_log_id = 123

    with patch.object(TaskLogService, "add", return_value=mock_task_log_id) as mock_add, \
         patch.object(TaskLogService, "update", return_value=None) as mock_update, \
         patch("app.arq_worker.AsyncSessionLocal") as mock_session_local, \
         patch("app.arq_worker.smooth_delay", return_value=None), \
         patch("app.arq_worker.get_db") as mock_get_db, \
         patch("app.arq_worker.send_error_notification") as mock_send_error_notification:

        # Мок сессии
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_session

        # Мок объекта Name
        mock_name = MagicMock(spec=Name)
        mock_session.get.return_value = mock_name

        # Мок оркестратора
        mock_orchestrator = AsyncMock(spec=ParserOrchestrator)
        mock_orchestrator._fill_rawdata_for_name.return_value = False

        with patch("app.arq_worker.ParserOrchestrator", return_value=mock_orchestrator):
            # Ожидаем RuntimeError
            with pytest.raises(RuntimeError):
                await parse_rawdata_task(mock_ctx, mock_name_id)

            # Проверки
            mock_add.assert_called_once_with(
                task_name="parse_rawdata_task",
                job_id="test_job_id",
                name_id=mock_name_id,
                session=mock_get_db
            )
            mock_update.assert_called_once_with(
                mock_task_log_id,
                'failed',
                "Failed to fill rawdata",
                session=mock_get_db
            )
            mock_session.rollback.assert_called_once()
            mock_send_error_notification.assert_called_once_with("Failed to fill rawdata")


@pytest.mark.asyncio
async def test_parse_rawdata_task_timeout():
    """Тест таймаута при выполнении задачи parse_rawdata_task"""
    # Подготовка моков
    mock_ctx = {"job_id": "test_job_id"}
    mock_name_id = 1
    mock_task_log_id = 123

    with patch.object(TaskLogService, "add", return_value=mock_task_log_id) as mock_add, \
         patch.object(TaskLogService, "update", return_value=None) as mock_update, \
         patch("app.arq_worker.AsyncSessionLocal") as mock_session_local, \
         patch("app.arq_worker.smooth_delay", return_value=None), \
         patch("app.arq_worker.get_db") as mock_get_db, \
         patch("app.arq_worker.send_error_notification") as mock_send_error_notification:

        # Мок сессии
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_session

        # Мок объекта Name
        mock_name = MagicMock(spec=Name)
        mock_session.get.return_value = mock_name

        # Мок оркестратора
        mock_orchestrator = AsyncMock(spec=ParserOrchestrator)
        # Создаем исключение asyncio.TimeoutError
        mock_orchestrator._fill_rawdata_for_name.side_effect = asyncio.TimeoutError()

        with patch("app.arq_worker.ParserOrchestrator", return_value=mock_orchestrator):
            # Вызов тестируемой функции (ожидаем, что ошибка будет обработана)
            await parse_rawdata_task(mock_ctx, mock_name_id)

            # Проверки
            mock_add.assert_called_once_with(
                task_name="parse_rawdata_task",
                job_id="test_job_id",
                name_id=mock_name_id,
                session=mock_get_db
            )
            mock_update.assert_called_once_with(
                mock_task_log_id,
                'failed',
                "TimeoutError()",
                session=mock_get_db
            )
            mock_send_error_notification.assert_called_once_with("TimeoutError()")


@pytest.mark.asyncio
async def test_parse_rawdata_task_name_not_found():
    """Тест случая, когда объект Name не найден"""
    # Подготовка моков
    mock_ctx = {"job_id": "test_job_id"}
    mock_name_id = 1
    mock_task_log_id = 123

    with patch.object(TaskLogService, "add", return_value=mock_task_log_id) as mock_add, \
         patch.object(TaskLogService, "update", return_value=None) as mock_update, \
         patch("app.arq_worker.AsyncSessionLocal") as mock_session_local, \
         patch("app.arq_worker.smooth_delay", return_value=None), \
         patch("app.arq_worker.get_db") as mock_get_db, \
         patch("app.arq_worker.send_error_notification") as mock_send_error_notification:

        # Мок сессии
        mock_session = AsyncMock(spec=AsyncSession)
        mock_session_local.return_value.__aenter__.return_value = mock_session
        mock_get_db.return_value = mock_session

        # Мок объекта Name (None, т.е. не найден)
        mock_session.get.return_value = None

        # Вызов тестируемой функции
        with pytest.raises(ValueError, match="Name not found"):
            await parse_rawdata_task(mock_ctx, mock_name_id)

        # Проверки
        mock_add.assert_called_once_with(
            task_name="parse_rawdata_task",
            job_id="test_job_id",
            name_id=mock_name_id,
            session=mock_get_db
        )
        mock_update.assert_called_once_with(
            mock_task_log_id,
            'failed',
            "Name not found",
            session=mock_get_db
        )
        mock_send_error_notification.assert_called_once_with("Name not found")