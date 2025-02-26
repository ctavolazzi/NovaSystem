"""
Unit tests for the Nova API router endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from unittest.mock import MagicMock, patch, AsyncMock
import json
import sys
import os
from datetime import datetime

# Add the correct path to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../')))

# Import using correct paths
from backend.api.routers.nova import router
from backend.nova_process import NovaProcessManager, ProcessStage


@pytest.fixture
def mock_session_manager():
    """Returns a mock session manager for testing."""
    mock = MagicMock()
    mock.get_session.return_value = {
        "id": "test-session-456",
        "user_id": "user-789",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "messages": []
    }
    mock.add_message.return_value = True
    return mock


@pytest.fixture
def mock_process_manager():
    """Returns a mock process manager for testing."""
    mock = MagicMock(spec=NovaProcessManager)

    # Mock the expected methods
    mock.start_iteration = AsyncMock()
    # Ensure the AsyncMock immediately returns its result without hanging
    mock.start_iteration.return_value = {
        "id": "test-iteration-123",
        "session_id": "test-session-456",
        "number": 1,
        "problem_statement": "How to improve user engagement?",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {
            ProcessStage.PROBLEM_UNPACKING.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Problem unpacking result"
            }
        },
        "required_experts": [],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    mock.get_iteration = AsyncMock()
    mock.get_iteration.return_value = {
        "id": "test-iteration-123",
        "session_id": "test-session-456",
        "number": 1,
        "problem_statement": "How to improve user engagement?",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {
            ProcessStage.PROBLEM_UNPACKING.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Problem unpacking result"
            },
            ProcessStage.EXPERTISE_ASSEMBLY.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Expertise assembly result"
            }
        },
        "required_experts": ["UX Research", "Product Management"],
        "expertise_contributions": {
            "UX Research": "UX research contribution",
            "Product Management": "Product management contribution"
        },
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    mock.continue_iteration = AsyncMock()
    mock.continue_iteration.return_value = {
        "id": "test-iteration-123",
        "session_id": "test-session-456",
        "number": 1,
        "problem_statement": "How to improve user engagement?",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {
            ProcessStage.PROBLEM_UNPACKING.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Problem unpacking result"
            },
            ProcessStage.EXPERTISE_ASSEMBLY.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Expertise assembly result"
            },
            ProcessStage.COLLABORATIVE_IDEATION.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Collaborative ideation result"
            }
        },
        "required_experts": ["UX Research", "Product Management"],
        "expertise_contributions": {
            "UX Research": "UX research contribution",
            "Product Management": "Product management contribution"
        },
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    mock.list_iterations = MagicMock()
    mock.list_iterations.return_value = [
        {
            "id": "iteration-1",
            "session_id": "test-session-456",
            "number": 1,
            "problem_statement": "How to improve user engagement?",
            "start_time": datetime.utcnow().isoformat(),
            "stages": {
                ProcessStage.PROBLEM_UNPACKING.value: {
                    "completed_at": datetime.utcnow().isoformat(),
                    "result": "Problem unpacking result"
                }
            },
            "required_experts": [],
            "expertise_contributions": {},
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        },
        {
            "id": "iteration-2",
            "session_id": "test-session-456",
            "number": 2,
            "problem_statement": "How to improve customer satisfaction?",
            "start_time": datetime.utcnow().isoformat(),
            "stages": {
                ProcessStage.PROBLEM_UNPACKING.value: {
                    "completed_at": datetime.utcnow().isoformat(),
                    "result": "Problem unpacking result"
                },
                ProcessStage.EXPERTISE_ASSEMBLY.value: {
                    "completed_at": datetime.utcnow().isoformat(),
                    "result": "Expertise assembly result"
                }
            },
            "required_experts": ["UX Research", "Product Management"],
            "expertise_contributions": {
                "UX Research": "UX research contribution",
                "Product Management": "Product management contribution"
            },
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }
    ]

    return mock


@pytest.fixture
def app(mock_process_manager, mock_session_manager, monkeypatch):
    """Creates a FastAPI app with the nova router for testing."""
    app = FastAPI()

    # Override dependencies
    from backend.api.routers.nova import get_session_by_id, get_iteration_by_id
    import backend.api.routers.nova as nova_module

    # Apply monkeypatching for router-level dependencies
    monkeypatch.setattr(nova_module, "nova_process_manager", mock_process_manager)
    monkeypatch.setattr(nova_module, "session_manager", mock_session_manager)

    # Create dependency overrides
    async def override_get_session_by_id(session_id: str):
        return mock_session_manager.get_session(session_id)

    async def override_get_iteration_by_id(session_id: str, iteration_id: str):
        # Use the awaitable mock
        return await mock_process_manager.get_iteration(session_id, iteration_id)

    # Apply dependency overrides
    app.dependency_overrides[get_session_by_id] = override_get_session_by_id
    app.dependency_overrides[get_iteration_by_id] = override_get_iteration_by_id

    # Include the router
    app.include_router(router)

    return app


@pytest.fixture
def client(app):
    """Returns a test client for the FastAPI app."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_start_iteration(client, mock_process_manager, mock_session_manager):
    """Test the start iteration endpoint."""
    # Prepare test data
    session_id = "test-session-456"
    payload = {
        "problem_statement": "How to improve user engagement?"
    }

    # Create a pre-defined response
    iteration_result = {
        "id": "test-iteration-123",
        "session_id": session_id,
        "number": 1,
        "problem_statement": "How to improve user engagement?",
        "start_time": datetime.utcnow().isoformat(),
        "stages": {
            ProcessStage.PROBLEM_UNPACKING.value: {
                "completed_at": datetime.utcnow().isoformat(),
                "result": "Problem unpacking result"
            }
        },
        "required_experts": [],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None,
        "complete": False
    }

    # Update the mock to return our pre-defined response
    mock_process_manager.start_iteration.return_value = iteration_result

    # Call endpoint (no need for timeout, it shouldn't hang now)
    response = client.post(f"/nova/sessions/{session_id}/iterations", json=payload)

    # Assertions
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == "test-iteration-123"
    assert result["number"] == 1
    assert result["problem_statement"] == "How to improve user engagement?"
    assert ProcessStage.PROBLEM_UNPACKING.value in result["stages"]

    # Verify mock calls
    mock_process_manager.start_iteration.assert_called_once_with(
        session_id=session_id,
        problem_statement=payload["problem_statement"]
    )
    mock_session_manager.add_message.assert_called_once()


@pytest.mark.asyncio
async def test_get_iteration(client, mock_process_manager, mock_session_manager):
    """Test the get iteration endpoint."""
    # Call endpoint
    session_id = "test-session-456"
    iteration_id = "test-iteration-123"
    response = client.get(f"/nova/sessions/{session_id}/iterations/{iteration_id}")

    # Assertions
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == iteration_id
    assert result["number"] == 1
    assert len(result["stages"]) == 2  # Has both problem_unpacking and expertise_assembly stages

    # Verify mock calls
    mock_process_manager.get_iteration.assert_called_with(session_id, iteration_id)


@pytest.mark.asyncio
async def test_continue_iteration(client, mock_process_manager, mock_session_manager):
    """Test the continue iteration endpoint."""
    # Call endpoint
    session_id = "test-session-456"
    iteration_id = "test-iteration-123"
    response = client.post(f"/nova/sessions/{session_id}/iterations/{iteration_id}/continue")

    # Assertions
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == iteration_id
    assert result["number"] == 1
    assert ProcessStage.COLLABORATIVE_IDEATION.value in result["stages"]

    # Verify mock calls
    mock_process_manager.continue_iteration.assert_called_once_with(
        session_id=session_id,
        iteration_id=iteration_id
    )
    mock_session_manager.add_message.assert_called_once()


@pytest.mark.asyncio
async def test_list_iterations(client, mock_process_manager, mock_session_manager):
    """Test the list iterations endpoint."""
    # Call endpoint
    session_id = "test-session-456"
    response = client.get(f"/nova/sessions/{session_id}/iterations")

    # Assertions
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2
    assert result[0]["id"] == "iteration-1"
    assert result[1]["id"] == "iteration-2"

    # Verify mock calls
    mock_process_manager.list_iterations.assert_called_once_with(session_id)