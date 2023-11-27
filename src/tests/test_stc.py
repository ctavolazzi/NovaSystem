import pytest
from src.utils.stream_to_console import stream_to_console as stc

def test_stc():
    # Simple test to check if stream_to_console works as expected
    # This is a basic test and can be expanded to check for more specific functionalities
    assert stc("Test message", delay=0.01) is None  # stc function does not return a value
