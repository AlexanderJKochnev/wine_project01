#!/usr/bin/env python3
"""
Test script to verify that the ARQ worker fixes work properly
"""
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from app.arq_worker import parse_rawdata_task
from app.support.parser.service import TaskLogService
from app.support.parser.model import Name, TaskLog
from sqlalchemy.ext.asyncio import AsyncSession


async def test_worker_function():
    print("Testing ARQ worker function...")
    
    # Create a mock context and name_id
    mock_ctx = {"job_id": "test_job_123"}
    name_id = 1
    
    # Mock the AsyncSessionLocal context manager
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    
    # Mock the name object that will be returned by session.get()
    mock_name = MagicMock(spec=Name)
    mock_name.id = name_id
    
    with patch('app.arq_worker.AsyncSessionLocal') as mock_session_local, \
         patch('app.arq_worker.ParserOrchestrator') as mock_orchestrator_class, \
         patch('app.arq_worker.send_error_notification') as mock_email:
        
        # Configure the mock session factory to return our mock session
        mock_session_local.return_value = mock_session
        
        # Configure the mock session.get() to return the mock name
        mock_session.get.return_value = mock_name
        
        # Configure the orchestrator mock
        mock_orchestrator = AsyncMock()
        mock_orchestrator._fill_rawdata_for_name = AsyncMock(return_value=True)
        mock_orchestrator_class.return_value = mock_orchestrator
        
        # Mock TaskLogService methods
        with patch.object(TaskLogService, 'add_with_session', new_callable=AsyncMock) as mock_add, \
             patch.object(TaskLogService, 'update_with_session', new_callable=AsyncMock) as mock_update:
            
            mock_add.return_value = 123  # Return a task log ID
            
            # Test the function - this should not raise an error about 'function' object has no attribute 'add'
            try:
                await parse_rawdata_task(mock_ctx, name_id)
                print("✓ ARQ worker function executed successfully without the original error")
                print("✓ TaskLogService.add_with_session was called properly")
                print("✓ TaskLogService.update_with_session was called properly")
                
                # Verify that the correct methods were called
                assert mock_add.called, "TaskLogService.add_with_session should have been called"
                assert mock_orchestrator._fill_rawdata_for_name.called, "Orchestrator method should have been called"
                assert mock_update.called, "TaskLogService.update_with_session should have been called"
                
                print("✓ All expected method calls were made")
                
            except AttributeError as e:
                if "'function' object has no attribute 'add'" in str(e):
                    print(f"✗ Original error still exists: {e}")
                    return False
                else:
                    print(f"✗ Different AttributeError occurred: {e}")
                    return False
            except Exception as e:
                print(f"✗ Unexpected error occurred: {e}")
                return False
    
    print("✓ All tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_worker_function())
    if success:
        print("\n🎉 All fixes are working correctly!")
    else:
        print("\n❌ Some issues remain.")
        exit(1)