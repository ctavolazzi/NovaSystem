import pytest
from unittest.mock import MagicMock
import sys
import os
from pathlib import Path

# Add the NS-bytesize utils directory to the Python path
ns_bytesize_utils_path = Path(__file__).parent.parent / "dev" / "NS-bytesize" / "utils"
if str(ns_bytesize_utils_path) not in sys.path:
    sys.path.insert(0, str(ns_bytesize_utils_path))

# Now import the OllamaValidator class
from ollama_validator import OllamaValidator

@pytest.fixture
def mock_requests(monkeypatch):
    """Mock the requests.get method."""
    mock = MagicMock()
    monkeypatch.setattr("requests.get", mock)
    return mock

def test_host_property(mock_requests):
    """Test the host property."""
    validator = OllamaValidator()

    # Setup successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_requests.return_value = mock_response

    # Should return host when valid
    assert validator.host == "http://localhost:11434"  # Using default localhost