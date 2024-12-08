import pytest
from unittest.mock import patch
from io import StringIO
from utils.console import NovaConsole, MessageType, ConsoleColor
import re
from datetime import datetime

def strip_ansi(text):
    """Remove ANSI escape sequences from text"""
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

@pytest.fixture
def console():
    return NovaConsole(show_timestamp=False)  # Disable timestamp for predictable output

@pytest.fixture
def debug_console():
    return NovaConsole(show_timestamp=False, debug=True)

def test_basic_message_formatting(console):
    """Test basic message formatting without timestamp"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        console.info("Test message")
        output = strip_ansi(fake_out.getvalue().strip())
        assert "INFO: Test message" == output

def test_message_with_detail(console):
    """Test message formatting with detail"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        console.info("Test message", detail={"key": "value"})
        output = strip_ansi(fake_out.getvalue())
        assert "INFO: Test message" in output
        assert "Detail: {'key': 'value'}" in output

def test_all_message_types(console):
    """Test all message types"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        console.info("Info message")
        console.success("Success message")
        console.warning("Warning message")
        console.error("Error message")
        console.system("System message")

        output = strip_ansi(fake_out.getvalue())
        assert "INFO: Info message" in output
        assert "SUCCESS: Success message" in output
        assert "WARNING: Warning message" in output
        assert "ERROR: Error message" in output
        assert "SYSTEM: System message" in output

def test_debug_messages(console, debug_console):
    """Test debug messages with debug mode on and off"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        # Regular console (debug=False)
        console.debug("Debug message")
        assert fake_out.getvalue() == ""  # No output for debug=False

        # Debug console (debug=True)
        debug_console.debug("Debug message")
        output = strip_ansi(fake_out.getvalue().strip())
        assert "DEBUG: Debug message" == output

def test_timestamp_formatting():
    """Test timestamp formatting"""
    console = NovaConsole(show_timestamp=True)
    current_time = datetime.now().strftime('%H:%M:%S')

    with patch('sys.stdout', new=StringIO()) as fake_out:
        console.info("Test message")
        output = strip_ansi(fake_out.getvalue())
        assert current_time[:5] in output

def test_progress_bar(console):
    """Test progress bar display"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        console.progress(5, 10, prefix="Processing", suffix="Complete")
        output = strip_ansi(fake_out.getvalue())
        assert "Processing" in output
        assert "50.0%" in output
        assert "Complete" in output

def test_clear_console(console):
    """Test console clearing"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        console.clear()
        assert '\033[H\033[J' in fake_out.getvalue()