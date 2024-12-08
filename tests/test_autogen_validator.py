import pytest
import json

@pytest.fixture
def temp_config_file_openai(tmp_path):
    """Create a temporary config file for OpenAI testing."""
    config_file = tmp_path / "autogen_openai_config.json"
    config = {
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 2000,
        "seed": 123
    }
    config_file.write_text(json.dumps(config))
    return config_file

@pytest.fixture
def temp_config_file_ollama(tmp_path):
    """Create a temporary config file for Ollama testing."""
    config_file = tmp_path / "autogen_ollama_config.json"
    config = {
        "model": "llama3.2",
        "temperature": 0.7,
        "num_predict": 2000,
        "seed": 123
    }
    config_file.write_text(json.dumps(config))
    return config_file

def test_custom_config_path_ollama(temp_config_file_ollama):
    """Test initialization with custom config file path for Ollama."""
    validator = AutogenValidator(backend="ollama", config_path=temp_config_file_ollama)
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "llama3.2"  # Using llama3.2 as requested

def test_custom_config_path_openai(temp_config_file_openai):
    """Test initialization with custom config file path for OpenAI."""
    validator = AutogenValidator(backend="openai", config_path=temp_config_file_openai)
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "gpt-4o"  # Using gpt-4o as requested

def test_status_output(temp_config_file_openai, capsys):
    """Test status method output."""
    validator = AutogenValidator(
        backend="openai",
        config_path=temp_config_file_openai
    )
    validator.status()
    captured = capsys.readouterr()
    assert "=== Autogen Configuration Status (openai) ===" in captured.out
    assert "✅ Valid configuration loaded" in captured.out
    assert "Model: gpt-4o" in captured.out  # Using gpt-4o as requested