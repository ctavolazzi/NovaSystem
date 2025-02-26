"""
Session management module.

This module provides functionality for managing user sessions
with the NovaSystem.
"""
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manager for user sessions.

    This class manages sessions, which represent user conversations
    and interactions with the system.
    """

    def __init__(self):
        """Initialize the session manager."""
        self.sessions = {}  # Maps session_id to session data
        self.user_sessions = {}  # Maps user_id to list of session_ids

    def create_session(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new session.

        Args:
            user_id: Optional ID of the user creating the session.

        Returns:
            Dictionary containing session data.
        """
        session_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()

        # Create session data
        session = {
            "id": session_id,
            "user_id": user_id,
            "created_at": created_at,
            "last_active": created_at,
            "name": f"Session {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            "messages": []
        }

        # Store in our data structures
        self.sessions[session_id] = session

        # If user_id is provided, add to user's sessions
        if user_id:
            user_sessions = self.user_sessions.get(user_id, [])
            user_sessions.append(session_id)
            self.user_sessions[user_id] = user_sessions

        logger.info(f"Created session {session_id} for user {user_id or 'anonymous'}")
        return session

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a session by ID.

        Args:
            session_id: The ID of the session to get.

        Returns:
            Dictionary containing session data, or None if not found.
        """
        return self.sessions.get(session_id)

    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List sessions, optionally filtered by user ID.

        Args:
            user_id: Optional user ID to filter by.

        Returns:
            List of session data dictionaries.
        """
        if user_id:
            # Return sessions for a specific user
            session_ids = self.user_sessions.get(user_id, [])
            return [self.sessions[session_id] for session_id in session_ids
                    if session_id in self.sessions]
        else:
            # Return all sessions
            return list(self.sessions.values())

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: The ID of the session to delete.

        Returns:
            True if session was deleted, False otherwise.
        """
        if session_id not in self.sessions:
            return False

        # Get the user_id before deleting
        user_id = self.sessions[session_id].get("user_id")

        # Delete from sessions dict
        del self.sessions[session_id]

        # If associated with a user, remove from user_sessions
        if user_id and user_id in self.user_sessions:
            if session_id in self.user_sessions[user_id]:
                self.user_sessions[user_id].remove(session_id)

                # If user has no more sessions, clean up
                if not self.user_sessions[user_id]:
                    del self.user_sessions[user_id]

        logger.info(f"Deleted session {session_id}")
        return True

    def add_message(self, session_id: str, role: str, content: str,
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Add a message to a session.

        Args:
            session_id: The ID of the session.
            role: The role of the message sender (e.g., 'user', 'assistant', 'system').
            content: The content of the message.
            metadata: Optional metadata for the message.

        Returns:
            The added message, or None if session not found.
        """
        session = self.sessions.get(session_id)
        if not session:
            return None

        # Create message
        message = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }

        # Add to session messages
        session["messages"].append(message)

        # Update last active timestamp
        session["last_active"] = datetime.utcnow().isoformat()

        return message

    def get_messages(self, session_id: str, limit: Optional[int] = None,
                    before_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get messages from a session.

        Args:
            session_id: The ID of the session.
            limit: Optional limit on number of messages to return.
            before_id: Optional message ID to get messages before.

        Returns:
            List of message dictionaries, or empty list if session not found.
        """
        session = self.sessions.get(session_id)
        if not session:
            return []

        messages = session.get("messages", [])

        # If before_id is provided, filter messages
        if before_id:
            try:
                index = next(i for i, m in enumerate(messages) if m["id"] == before_id)
                messages = messages[:index]
            except StopIteration:
                # Message not found, return all messages
                pass

        # Apply limit if provided
        if limit is not None and limit > 0:
            messages = messages[-limit:]

        return messages

    def rename_session(self, session_id: str, name: str) -> bool:
        """
        Rename a session.

        Args:
            session_id: The ID of the session to rename.
            name: The new name for the session.

        Returns:
            True if session was renamed, False otherwise.
        """
        session = self.sessions.get(session_id)
        if not session:
            return False

        session["name"] = name
        return True