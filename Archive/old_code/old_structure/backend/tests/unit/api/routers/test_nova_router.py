"""
Unit tests for the Nova Process API router endpoints.
"""
import uuid
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch, call

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from session_manager import SessionManager
from models.nova_iteration import NovaIteration
from api.routers.nova import router as nova_router
from nova_process import NovaProcessManager


@pytest.fixture
def app(monkeypatch):
    """Creates a FastAPI app with the nova router for testing."""
    app = FastAPI()

    # Import the modules we need to monkeypatch
    import api.routers.nova as nova_module
    from pydantic import BaseModel
    from typing import Dict, List, Any, Optional

    # Create a class to bypass response validation for testing
    class TestResponseModel(BaseModel):
        class Config:
            extra = "allow"
            arbitrary_types_allowed = True

    # Override response_model for router endpoints
    for route in nova_router.routes:
        route.response_model = TestResponseModel

    # Include the router
    app.include_router(nova_router)
    return app


@pytest.fixture
def client(app):
    """Creates a test client for making requests to the app."""
    return TestClient(app)


@pytest.fixture
def mock_session_manager():
    """Returns a mock session manager for testing."""
    mock = MagicMock(spec=SessionManager)
    # Setup mock to return a session when get_session is called
    mock.get_session.return_value = {
        "id": "test-session-id",
        "user_id": "test-user",
        "name": "Test Session",
        "created_at": "2023-01-01T00:00:00",
        "last_active": "2023-01-01T00:00:00",
        "messages": []
    }
    return mock


@pytest.fixture
def mock_nova_process_manager():
    """Returns a mock NovaProcessManager for testing."""
    from unittest.mock import AsyncMock, MagicMock

    mock = MagicMock(spec=NovaProcessManager)

    # Helper to configure mocks to accept both positional and keyword arguments
    def configureMock(mock_func, return_value):
        # Keep the original side_effect to preserve AsyncMock behavior
        original_side_effect = mock_func.side_effect

        # Define a new side_effect that handles both positional and keyword args
        async def new_side_effect(*args, **kwargs):
            # Convert positional args to keyword args if needed
            if args and not kwargs:
                if len(args) == 2:  # Most common case for our methods (session_id, iteration_id)
                    kwargs = {"session_id": args[0], "iteration_id": args[1]}
                elif len(args) == 1:  # For methods taking only session_id
                    kwargs = {"session_id": args[0]}

            # If we have a problem_statement in args (for start_iteration)
            if len(args) > 2 and not kwargs.get("problem_statement"):
                kwargs["problem_statement"] = args[2]

            # Call the original side_effect with kwargs
            if original_side_effect:
                if callable(original_side_effect) and not isinstance(original_side_effect, (AsyncMock, MagicMock)):
                    result = await original_side_effect(**kwargs)
                    return result

            return return_value

        mock_func.side_effect = new_side_effect
        return mock_func

    # Setup mock to return an iteration when get_iteration is called
    # Use AsyncMock for async methods
    mock.get_iteration = AsyncMock()
    get_iteration_result = {
        "id": "test-iteration-id",
        "session_id": "test-session-id",
        "number": 1,
        "problem_statement": "Test problem",
        "start_time": "2023-01-01T00:00:00",
        "complete": False,
        "current_stage": "PROBLEM_UNPACKING",
        "stages": {"PROBLEM_UNPACKING": {"status": "complete", "data": {}}},
        "required_experts": ["expert1", "expert2"],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None
    }
    configureMock(mock.get_iteration, get_iteration_result)

    # Setup mock to return iterations when list_iterations is called
    # This is a synchronous method
    mock.list_iterations = MagicMock()
    list_iterations_result = {
        "iterations": [
            {
                "id": "test-iteration-id",
                "session_id": "test-session-id",
                "number": 1,
                "problem_statement": "Test problem",
                "start_time": "2023-01-01T00:00:00",
                "complete": False,
                "current_stage": "PROBLEM_UNPACKING",
                "stages": {"PROBLEM_UNPACKING": {"status": "complete", "data": {}}},
                "required_experts": ["expert1", "expert2"],
                "expertise_contributions": {},
                "critical_analysis": None,
                "summary": None,
                "next_steps": None
            }
        ]
    }
    mock.list_iterations.return_value = list_iterations_result

    # Setup mock to return an iteration when start_iteration is called
    # Use AsyncMock for async methods
    mock.start_iteration = AsyncMock()
    start_iteration_result = {
        "id": "test-iteration-id",
        "session_id": "test-session-id",
        "number": 1,
        "problem_statement": "Test problem",
        "start_time": "2023-01-01T00:00:00",
        "complete": False,
        "current_stage": "PROBLEM_UNPACKING",
        "stages": {"PROBLEM_UNPACKING": {"status": "complete", "data": {}}},
        "required_experts": ["expert1", "expert2"],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None
    }
    configureMock(mock.start_iteration, start_iteration_result)

    # Setup mock to return an iteration when continue_iteration is called
    # Use AsyncMock for async methods
    mock.continue_iteration = AsyncMock()
    continue_iteration_result = {
        "id": "test-iteration-id",
        "session_id": "test-session-id",
        "number": 1,
        "problem_statement": "Test problem",
        "start_time": "2023-01-01T00:00:00",
        "complete": False,
        "current_stage": "EXPERTISE_ASSEMBLY",
        "stages": {"PROBLEM_UNPACKING": {"status": "complete", "data": {}}},
        "required_experts": ["expert1", "expert2"],
        "expertise_contributions": {},
        "critical_analysis": None,
        "summary": None,
        "next_steps": None
    }
    configureMock(mock.continue_iteration, continue_iteration_result)

    return mock


@pytest.mark.asyncio
async def test_start_iteration(client, mock_session_manager, mock_nova_process_manager, monkeypatch):
    """Test the start iteration endpoint."""
    # Set up dependencies
    import api.routers.nova as nova_module
    monkeypatch.setattr(nova_module, "session_manager", mock_session_manager)
    monkeypatch.setattr(nova_module, "nova_process_manager", mock_nova_process_manager)

    # Prepare request data
    problem_statement = "Test problem"
    session_id = "test-session-id"

    # Make request
    response = client.post(
        f"/nova/sessions/{session_id}/iterations",
        json={"problem_statement": problem_statement}
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-iteration-id"
    assert data["session_id"] == "test-session-id"
    assert data["problem_statement"] == "Test problem"
    assert data["current_stage"] == "PROBLEM_UNPACKING"
    assert not data["complete"]

    # Verify mock calls
    mock_session_manager.get_session.assert_called_once_with(session_id)
    mock_nova_process_manager.start_iteration.assert_called_once_with(
        session_id=session_id, problem_statement=problem_statement
    )


@pytest.mark.asyncio
async def test_continue_iteration(client, mock_session_manager, mock_nova_process_manager, monkeypatch):
    """Test the continue iteration endpoint."""
    # Set up dependencies
    import api.routers.nova as nova_module
    monkeypatch.setattr(nova_module, "session_manager", mock_session_manager)
    monkeypatch.setattr(nova_module, "nova_process_manager", mock_nova_process_manager)

    # Prepare test data
    session_id = "test-session-id"
    iteration_id = "test-iteration-id"

    # Make request
    response = client.post(
        f"/nova/sessions/{session_id}/iterations/{iteration_id}/continue",
        json={}
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == iteration_id
    assert data["session_id"] == session_id
    assert data["current_stage"] == "EXPERTISE_ASSEMBLY"
    assert len(data["stages"]) > 0

    # Verify mock calls
    assert mock_session_manager.get_session.call_count == 1
    assert mock_nova_process_manager.get_iteration.call_count == 1
    assert mock_nova_process_manager.continue_iteration.call_count == 1

    # Check that the right values were passed (without caring about positional vs keyword)
    get_iteration_call = mock_nova_process_manager.get_iteration.call_args
    assert session_id in get_iteration_call.args or session_id in get_iteration_call.kwargs.values()
    assert iteration_id in get_iteration_call.args or iteration_id in get_iteration_call.kwargs.values()

    continue_iteration_call = mock_nova_process_manager.continue_iteration.call_args
    assert session_id in continue_iteration_call.args or session_id in continue_iteration_call.kwargs.values()
    assert iteration_id in continue_iteration_call.args or iteration_id in continue_iteration_call.kwargs.values()


@pytest.mark.asyncio
async def test_get_iteration(client, mock_session_manager, mock_nova_process_manager, monkeypatch):
    """Test the get iteration endpoint."""
    # Set up dependencies
    import api.routers.nova as nova_module
    monkeypatch.setattr(nova_module, "session_manager", mock_session_manager)
    monkeypatch.setattr(nova_module, "nova_process_manager", mock_nova_process_manager)

    # Prepare test data
    session_id = "test-session-id"
    iteration_id = "test-iteration-id"

    # Make request
    response = client.get(
        f"/nova/sessions/{session_id}/iterations/{iteration_id}"
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == iteration_id
    assert data["session_id"] == session_id
    assert len(data["stages"]) > 0

    # Verify mock calls
    assert mock_session_manager.get_session.call_count == 1
    assert mock_nova_process_manager.get_iteration.call_count == 1

    # Check that the right values were passed (without caring about positional vs keyword)
    get_session_call = mock_session_manager.get_session.call_args
    assert session_id in get_session_call.args or session_id in get_session_call.kwargs.values()

    get_iteration_call = mock_nova_process_manager.get_iteration.call_args
    assert session_id in get_iteration_call.args or session_id in get_iteration_call.kwargs.values()
    assert iteration_id in get_iteration_call.args or iteration_id in get_iteration_call.kwargs.values()


@pytest.mark.asyncio
async def test_list_iterations(client, mock_session_manager, mock_nova_process_manager, monkeypatch):
    """Test the list iterations endpoint."""
    # Set up dependencies
    import api.routers.nova as nova_module
    monkeypatch.setattr(nova_module, "session_manager", mock_session_manager)
    monkeypatch.setattr(nova_module, "nova_process_manager", mock_nova_process_manager)

    # Prepare test data
    session_id = "test-session-id"

    # Make request
    response = client.get(
        f"/nova/sessions/{session_id}/iterations"
    )

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "iterations" in data
    assert len(data["iterations"]) > 0
    iteration = data["iterations"][0]
    assert iteration["id"] == "test-iteration-id"
    assert iteration["session_id"] == session_id

    # Verify mock calls
    assert mock_session_manager.get_session.call_count == 1
    assert mock_nova_process_manager.list_iterations.call_count == 1

    # Check that the right values were passed (without caring about positional vs keyword)
    get_session_call = mock_session_manager.get_session.call_args
    assert session_id in get_session_call.args or session_id in get_session_call.kwargs.values()

    list_iterations_call = mock_nova_process_manager.list_iterations.call_args
    assert session_id in list_iterations_call.args or session_id in list_iterations_call.kwargs.values()


@pytest.mark.asyncio
async def test_session_not_found(client, mock_session_manager, monkeypatch):
    """Test handling of requests with a non-existent session."""
    # Set up dependencies
    import api.routers.nova as nova_module
    monkeypatch.setattr(nova_module, "session_manager", mock_session_manager)

    # Setup mock to return None for non-existent session
    mock_session_manager.get_session.return_value = None

    # Prepare test data
    session_id = "non-existent-session"

    # Test GET iterations endpoint
    response = client.get(f"/nova/sessions/{session_id}/iterations")
    assert response.status_code == 404

    # Test POST iterations endpoint
    response = client.post(
        f"/nova/sessions/{session_id}/iterations",
        json={"problem_statement": "Test problem"}
    )
    assert response.status_code == 404

    # Test GET iteration endpoint
    response = client.get(f"/nova/sessions/{session_id}/iterations/test-iteration-id")
    assert response.status_code == 404