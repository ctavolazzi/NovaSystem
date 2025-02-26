"""
Unit tests for the SessionManager class.
"""
import pytest
from backend.session_manager import SessionManager


def test_create_session(session_manager):
    """Test session creation with and without user_id."""
    # Test with user_id
    session_id = session_manager.create_session(user_id="user123", name="Test Session")
    assert session_id is not None
    assert session_id in session_manager.sessions
    assert session_manager.sessions[session_id]["user_id"] == "user123"
    assert session_manager.sessions[session_id]["name"] == "Test Session"

    # Test without user_id
    session_id2 = session_manager.create_session(name="Anonymous Session")
    assert session_id2 is not None
    assert session_id2 in session_manager.sessions
    assert session_manager.sessions[session_id2]["name"] == "Anonymous Session"


def test_get_session(session_manager):
    """Test retrieving a session by ID."""
    # Create a session
    session_id = session_manager.create_session(user_id="user123", name="Test Session")

    # Retrieve the session
    session = session_manager.get_session(session_id)
    assert session is not None
    assert session["id"] == session_id
    assert session["user_id"] == "user123"
    assert session["name"] == "Test Session"

    # Test retrieving a non-existent session
    non_existent_id = "non-existent-id"
    assert session_manager.get_session(non_existent_id) is None


def test_list_sessions(session_manager):
    """Test listing all sessions and filtering by user_id."""
    # Create sessions for different users
    session_id1 = session_manager.create_session(user_id="user1", name="User 1 Session")
    session_id2 = session_manager.create_session(user_id="user2", name="User 2 Session")
    session_id3 = session_manager.create_session(user_id="user1", name="User 1 Second Session")

    # Test listing all sessions
    all_sessions = session_manager.list_sessions()
    assert len(all_sessions) == 3

    # Test filtering by user_id
    user1_sessions = session_manager.list_sessions(user_id="user1")
    assert len(user1_sessions) == 2
    assert all(session["user_id"] == "user1" for session in user1_sessions)

    user2_sessions = session_manager.list_sessions(user_id="user2")
    assert len(user2_sessions) == 1
    assert user2_sessions[0]["user_id"] == "user2"


def test_delete_session(session_manager):
    """Test deleting a session."""
    # Create a session
    session_id = session_manager.create_session(user_id="user123", name="Test Session")

    # Verify it exists
    assert session_id in session_manager.sessions

    # Delete the session
    result = session_manager.delete_session(session_id)
    assert result is True
    assert session_id not in session_manager.sessions

    # Test deleting a non-existent session
    result = session_manager.delete_session("non-existent-id")
    assert result is False


def test_add_get_messages(session_manager):
    """Test adding and retrieving messages from a session."""
    # Create a session
    session_id = session_manager.create_session(user_id="user123", name="Test Session")

    # Add messages
    message1 = {"role": "user", "content": "Hello"}
    message2 = {"role": "assistant", "content": "Hi there"}
    message3 = {"role": "user", "content": "How are you?"}

    session_manager.add_message(session_id, message1)
    session_manager.add_message(session_id, message2)
    session_manager.add_message(session_id, message3)

    # Get all messages
    messages = session_manager.get_messages(session_id)
    assert len(messages) == 3
    assert messages[0]["content"] == "Hello"
    assert messages[1]["content"] == "Hi there"
    assert messages[2]["content"] == "How are you?"

    # Test limit parameter
    limited_messages = session_manager.get_messages(session_id, limit=2)
    assert len(limited_messages) == 2
    assert limited_messages[0]["content"] == "Hi there"
    assert limited_messages[1]["content"] == "How are you?"

    # Test after_id parameter
    after_messages = session_manager.get_messages(session_id, after_id=messages[0]["id"])
    assert len(after_messages) == 2
    assert after_messages[0]["content"] == "Hi there"
    assert after_messages[1]["content"] == "How are you?"


def test_rename_session(session_manager):
    """Test renaming a session."""
    # Create a session
    session_id = session_manager.create_session(user_id="user123", name="Original Name")

    # Verify original name
    assert session_manager.sessions[session_id]["name"] == "Original Name"

    # Rename the session
    result = session_manager.rename_session(session_id, "New Name")
    assert result is True
    assert session_manager.sessions[session_id]["name"] == "New Name"

    # Test renaming a non-existent session
    result = session_manager.rename_session("non-existent-id", "Any Name")
    assert result is False