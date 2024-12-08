# Standard library
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Third party
import pytest

# Local
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.ollama_validator import OllamaValidator

@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file for testing."""
    env_file = tmp_path / ".env"
    env_file.write_text("OLLAMA_HOST=http://test-host:11434")
    return env_file

@pytest.fixture
def mock_requests():
    """Mock requests to avoid actual network calls."""
    with patch('requests.get') as mock_get:
        yield mock_get

def test_default_initialization():
    """Test initialization with default values."""
    validator = OllamaValidator()
    assert validator._default_host == "http://localhost:11434"
    assert validator._host == "http://localhost:11434"

def test_custom_env_path(temp_env_file):
    """Test initialization with custom env file path."""
    validator = OllamaValidator(env_path=temp_env_file)
    assert validator._host == "http://test-host:11434"

def test_valid_url():
    """Test URL validation."""
    validator = OllamaValidator()

    # Test valid URLs
    validator._host = "http://localhost:11434"
    assert validator._is_valid_url() is True

    validator._host = "https://example.com:11434"
    assert validator._is_valid_url() is True

    # Test invalid URLs
    validator._host = "not-a-url"
    assert validator._is_valid_url() is False

    validator._host = "http://"
    assert validator._is_valid_url() is False

def test_service_running(mock_requests):
    """Test service availability checking."""
    validator = OllamaValidator()

    # Test successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"version": "0.1.0"}
    mock_requests.return_value = mock_response

    assert validator._is_service_running() is True

    # Test failed response
    mock_requests.side_effect = Exception("Connection error")
    assert validator._is_service_running() is False

def test_is_valid_property(mock_requests):
    """Test the is_valid property."""
    validator = OllamaValidator()

    # Setup successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    assert validator.is_valid is True

    # Test with invalid URL
    validator._host = "invalid-url"
    assert validator.is_valid is False

    # Test with service down
    validator._host = "http://localhost:11434"
    mock_requests.side_effect = Exception("Connection error")
    assert validator.is_valid is False

def test_host_property(mock_requests):
    """Test the host property."""
    validator = OllamaValidator()

    # Setup successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Test default host
    assert validator.host == validator._host

    # Should raise error when invalid
    mock_requests.side_effect = Exception("Connection error")
    with pytest.raises(ValueError, match="No valid Ollama service found at configured host"):
        _ = validator.host

def test_status_output(mock_requests, capsys):
    """Test status method output."""
    validator = OllamaValidator()

    # Test when service is running
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"version": "0.1.0"}
    mock_requests.return_value = mock_response

    validator.status()
    captured = capsys.readouterr()
    assert "✅ Ollama service running at:" in captured.out
    assert "Version: 0.1.0" in captured.out

    # Test when service is down
    mock_requests.side_effect = Exception("Connection error")
    validator.status()
    captured = capsys.readouterr()
    assert "❌ Ollama service not running at:" in captured.out

def test_search_tree(tmp_path):
    """Test .env file search in directory tree."""
    # Create a nested directory structure with .env file
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    env_file = tmp_path / "a" / ".env"
    env_file.write_text("OLLAMA_HOST=http://nested-test:11434")

    # Change to the nested directory and initialize validator
    os.chdir(nested_dir)
    validator = OllamaValidator()

    assert validator._host == "http://nested-test:11434"