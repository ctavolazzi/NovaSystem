"""
Unit tests for the NovaProcessManager.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import uuid
import sys
import os
from datetime import datetime

# Add the correct path to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import using correct paths
from backend.nova_process import NovaProcessManager, ProcessStage


@pytest.fixture
def process_manager():
    """Returns a process manager instance for testing."""
    return NovaProcessManager()


def test_process_manager_initialization():
    """Test the initialization of the process manager."""
    # Create the process manager
    manager = NovaProcessManager()

    # Assertions
    assert manager is not None
    assert hasattr(manager, 'sessions')
    assert hasattr(manager, 'iterations')
    assert hasattr(manager, 'session_iterations')

    # Initial collections should be empty
    assert manager.sessions == {}
    assert manager.iterations == {}
    assert manager.session_iterations == {}


@pytest.mark.asyncio
@patch('backend.nova_process.create_dce_agent')
async def test_start_iteration(mock_create_dce, process_manager):
    """Test starting a new iteration."""
    # Setup mock
    mock_dce = AsyncMock()
    mock_dce.process.return_value = {
        "response": "Problem analysis result"
    }
    mock_create_dce.return_value = mock_dce

    # Call start_iteration
    session_id = "test-session-123"
    problem_statement = "How to improve user engagement?"
    result = await process_manager.start_iteration(session_id, problem_statement)

    # Assertions
    assert result is not None
    assert result["session_id"] == session_id
    assert result["problem_statement"] == problem_statement
    assert result["number"] == 1
    assert "id" in result
    assert "start_time" in result
    assert ProcessStage.PROBLEM_UNPACKING.value in result["stages"]

    # Verify mock calls
    mock_create_dce.assert_called_once()
    mock_dce.process.assert_called_once()

    # Verify data structures
    assert result["id"] in process_manager.iterations
    assert session_id in process_manager.session_iterations
    assert result["id"] in process_manager.session_iterations[session_id]


@pytest.mark.asyncio
async def test_get_iteration(process_manager):
    """Test getting an iteration by ID."""
    # Setup - create test data
    session_id = "test-session-456"
    iteration_id = "test-iteration-789"

    # Mock iteration data
    iteration_data = {
        "id": iteration_id,
        "session_id": session_id,
        "number": 1,
        "problem_statement": "Test problem",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {},
        "required_experts": [],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    # Directly add the test data to the manager
    process_manager.iterations[iteration_id] = iteration_data
    process_manager.session_iterations[session_id] = [iteration_id]

    # Call get_iteration
    result = await process_manager.get_iteration(session_id, iteration_id)

    # Assertions
    assert result is not None
    assert result == iteration_data
    assert result["id"] == iteration_id
    assert result["session_id"] == session_id

    # Test with invalid session
    invalid_result = await process_manager.get_iteration("wrong-session", iteration_id)
    assert invalid_result is None

    # Test with invalid iteration
    invalid_result = await process_manager.get_iteration(session_id, "wrong-iteration")
    assert invalid_result is None


def test_list_iterations(process_manager):
    """Test listing iterations for a session."""
    # Setup - create test data
    session_id = "test-session-list"
    iterations = [
        {
            "id": f"iteration-{i}",
            "session_id": session_id,
            "number": i+1,
            "problem_statement": f"Problem {i+1}",
            "start_time": datetime.utcnow().isoformat(),
            "stages": {},
            "required_experts": [],
            "expertise_contributions": {},
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }
        for i in range(3)
    ]

    # Directly add the test data to the manager
    iteration_ids = []
    for iteration in iterations:
        iteration_id = iteration["id"]
        iteration_ids.append(iteration_id)
        process_manager.iterations[iteration_id] = iteration

    process_manager.session_iterations[session_id] = iteration_ids

    # Call list_iterations
    result = process_manager.list_iterations(session_id)

    # Assertions
    assert result is not None
    assert len(result) == 3
    assert result[0]["id"] == "iteration-0"
    assert result[1]["id"] == "iteration-1"
    assert result[2]["id"] == "iteration-2"

    # Test with empty session
    empty_result = process_manager.list_iterations("non-existent-session")
    assert empty_result == []


@pytest.mark.asyncio
@patch('backend.nova_process.create_dce_agent')
@patch('backend.nova_process.create_domain_expert_agent')
@patch('backend.nova_process.create_cae_agent')
async def test_execute_stage(mock_create_cae, mock_create_domain_expert, mock_create_dce, process_manager):
    """Test executing different stages of the process."""
    # Setup mocks
    mock_dce = AsyncMock()
    mock_dce.process.return_value = {"response": "DCE response"}
    mock_create_dce.return_value = mock_dce

    mock_domain_expert = AsyncMock()
    mock_domain_expert.process.return_value = {"response": "Domain expert response"}
    mock_create_domain_expert.return_value = mock_domain_expert

    mock_cae = AsyncMock()
    mock_cae.process.return_value = {"response": "CAE analysis response"}
    mock_create_cae.return_value = mock_cae

    # Setup test iteration
    iteration_id = "test-execute-stage"
    iteration = {
        "id": iteration_id,
        "session_id": "test-session-execute",
        "number": 1,
        "problem_statement": "Test problem for execution",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {
            ProcessStage.PROBLEM_UNPACKING.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Problem analysis result"
            }
        },
        "required_experts": ["Software Engineering", "UX Design"],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    process_manager.iterations[iteration_id] = iteration

    # Test EXPERTISE_ASSEMBLY stage
    await process_manager._execute_stage(iteration_id, ProcessStage.EXPERTISE_ASSEMBLY)

    # Assertions
    assert ProcessStage.EXPERTISE_ASSEMBLY.value in process_manager.iterations[iteration_id]["stages"]
    assert "completed_at" in process_manager.iterations[iteration_id]["stages"][ProcessStage.EXPERTISE_ASSEMBLY.value]
    assert "result" in process_manager.iterations[iteration_id]["stages"][ProcessStage.EXPERTISE_ASSEMBLY.value]

    # Verify mock calls
    mock_create_dce.assert_called()
    mock_dce.process.assert_called()


@pytest.mark.asyncio
@patch('backend.nova_process.NovaProcessManager._execute_stage')
async def test_continue_iteration(mock_execute_stage, process_manager):
    """Test continuing an iteration to the next stage."""
    # Setup test iteration
    session_id = "test-session-continue"
    iteration_id = "test-iteration-continue"

    iteration = {
        "id": iteration_id,
        "session_id": session_id,
        "number": 1,
        "problem_statement": "Test problem for continuation",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {
            ProcessStage.PROBLEM_UNPACKING.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Problem analysis result"
            }
        },
        "required_experts": [],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    process_manager.iterations[iteration_id] = iteration
    process_manager.session_iterations[session_id] = [iteration_id]

    # Call continue_iteration
    mock_execute_stage.return_value = None
    result = await process_manager.continue_iteration(session_id, iteration_id)

    # Assertions
    assert result is not None
    assert result["id"] == iteration_id

    # Verify mock calls
    mock_execute_stage.assert_called_once_with(iteration_id, ProcessStage.EXPERTISE_ASSEMBLY)

    # Test with invalid iteration
    with pytest.raises(ValueError, match=f"Iteration with ID wrong-iteration not found"):
        await process_manager.continue_iteration(session_id, "wrong-iteration")

    # Test with invalid session
    with pytest.raises(ValueError, match=f"Iteration {iteration_id} does not belong to session wrong-session"):
        await process_manager.continue_iteration("wrong-session", iteration_id)