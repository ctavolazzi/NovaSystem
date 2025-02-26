"""
Shared test fixtures for NovaSystem backend tests.
"""
import pytest
import sys
import os

# Let's attempt a direct import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from session_manager import SessionManager


@pytest.fixture
def session_manager():
    """
    Provides a clean session manager instance for tests.
    """
    manager = SessionManager()
    yield manager