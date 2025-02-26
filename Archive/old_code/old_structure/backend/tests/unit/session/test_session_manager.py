"""
Unit tests for the Session Manager component.
"""
import pytest
from unittest.mock import MagicMock, patch
import uuid
import sys
import os

# Add the correct path to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import using correct paths
from backend.session_manager import SessionManager


@pytest.fixture
def mock_db():
    """Returns a mock database connection for testing."""
    mock = MagicMock()
    mock.get_session.return_value = {
        "session_id": "test-session-123",
        "user_id": "user-456",
        "created_at": "2023-06-15T10:00:00Z",
        "updated_at": "2023-06-15T10:30:00Z",
        "status": "active",
        "data": {"key": "value"}
    }
    mock.create_session.return_value = "new-session-789"
    mock.update_session.return_value = True
    mock.delete_session.return_value = True
    mock.list_sessions.return_value = [
        {"session_id": "session-1", "user_id": "user-1", "status": "active"},
        {"session_id": "session-2", "user_id": "user-1", "status": "completed"}
    ]
    return mock


@pytest.fixture
def session_manager(mock_db):
    """Returns a session manager instance for testing."""
    return SessionManager(db_client=mock_db)


def test_session_manager_initialization():
    """Test the initialization of the session manager."""
    # Create a mock database client
    mock_db = MagicMock()

    # Create the session manager
    manager = SessionManager(db_client=mock_db)

    # Assertions
    assert manager is not None
    assert manager.db_client == mock_db


def test_get_session(session_manager, mock_db):
    """Test getting a session by ID."""
    # Call get_session
    session = session_manager.get_session("test-session-123")

    # Assertions
    assert session is not None
    assert session["session_id"] == "test-session-123"
    assert session["user_id"] == "user-456"
    assert session["status"] == "active"

    # Verify mock calls
    mock_db.get_session.assert_called_once_with("test-session-123")


def test_create_session(session_manager, mock_db):
    """Test creating a new session."""
    # Call create_session
    user_id = "user-456"
    data = {"initial": "data"}
    session_id = session_manager.create_session(user_id, data)

    # Assertions
    assert session_id == "new-session-789"

    # Verify mock calls
    mock_db.create_session.assert_called_once()
    call_args = mock_db.create_session.call_args[0]
    assert call_args[0] == user_id
    assert "initial" in call_args[1]
    assert call_args[1]["initial"] == "data"


def test_update_session(session_manager, mock_db):
    """Test updating an existing session."""
    # Call update_session
    session_id = "test-session-123"
    updates = {"status": "completed", "data": {"new": "value"}}
    result = session_manager.update_session(session_id, updates)

    # Assertions
    assert result is True

    # Verify mock calls
    mock_db.update_session.assert_called_once_with(session_id, updates)


def test_delete_session(session_manager, mock_db):
    """Test deleting a session."""
    # Call delete_session
    session_id = "test-session-123"
    result = session_manager.delete_session(session_id)

    # Assertions
    assert result is True

    # Verify mock calls
    mock_db.delete_session.assert_called_once_with(session_id)


def test_list_user_sessions(session_manager, mock_db):
    """Test listing sessions for a user."""
    # Call list_user_sessions
    user_id = "user-1"
    sessions = session_manager.list_user_sessions(user_id)

    # Assertions
    assert sessions is not None
    assert len(sessions) == 2
    assert sessions[0]["session_id"] == "session-1"
    assert sessions[0]["user_id"] == "user-1"
    assert sessions[1]["session_id"] == "session-2"

    # Verify mock calls
    mock_db.list_sessions.assert_called_once_with(user_id=user_id)


@patch("uuid.uuid4")
def test_generate_session_id(mock_uuid, session_manager):
    """Test generating a session ID."""
    # Setup mock
    mock_uuid.return_value = uuid.UUID("00000000-0000-0000-0000-000000000123")

    # Call _generate_session_id
    session_id = session_manager._generate_session_id()

    # Assertions
    assert session_id == "00000000-0000-0000-0000-000000000123"

    # Verify mock calls
    mock_uuid.assert_called_once()