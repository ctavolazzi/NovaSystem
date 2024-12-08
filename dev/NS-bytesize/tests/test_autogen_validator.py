# Standard library
import os
from pathlib import Path
import json

# Third party
import pytest

# Local
from utils.autogen_validator import AutogenValidator

@pytest.fixture
def temp_env_file_openai(tmp_path):
    """Create a temporary .env file for OpenAI testing."""
    env_file = tmp_path / ".env"
    env_file.write_text("""
AUTOGEN_MODEL=gpt-4o
AUTOGEN_TEMPERATURE=0.8
AUTOGEN_MAX_TOKENS=1500
AUTOGEN_SEED=42
""".strip())
    return env_file

@pytest.fixture
def temp_env_file_ollama(tmp_path):
    """Create a temporary .env file for Ollama testing."""
    env_file = tmp_path / ".env"
    env_file.write_text("""
AUTOGEN_OLLAMA_MODEL=llama3.2
AUTOGEN_OLLAMA_TEMPERATURE=0.8
AUTOGEN_OLLAMA_NUM_PREDICT=1500
AUTOGEN_OLLAMA_SEED=42
""".strip())
    return env_file

@pytest.fixture
def temp_config_file_openai(tmp_path):
    """Create a temporary config file for OpenAI testing."""
    config_file = tmp_path / "autogen_openai_config.json"
    config = {
        "model": "gpt-4o",
        "temperature": 0.8,
        "max_tokens": 1500,
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
        "temperature": 0.8,
        "num_predict": 1500,
        "seed": 123
    }
    config_file.write_text(json.dumps(config))
    return config_file

def test_default_initialization_openai():
    """Test initialization with default OpenAI values."""
    validator = AutogenValidator(backend="openai")
    assert not validator.is_valid  # Should be invalid without config

def test_default_initialization_ollama():
    """Test initialization with default Ollama values."""
    validator = AutogenValidator(backend="ollama")
    assert not validator.is_valid  # Should be invalid without config

def test_custom_env_path_openai(temp_env_file_openai):
    """Test initialization with custom env file path for OpenAI."""
    validator = AutogenValidator(backend="openai", env_path=temp_env_file_openai)
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "gpt-4o"
    assert config["temperature"] == 0.8
    assert config["max_tokens"] == 1500

def test_custom_env_path_ollama(temp_env_file_ollama):
    """Test initialization with custom env file path for Ollama."""
    validator = AutogenValidator(backend="ollama", env_path=temp_env_file_ollama)
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "llama3.2"
    assert config["temperature"] == 0.8
    assert config["num_predict"] == 1500

def test_custom_config_path_openai(temp_config_file_openai):
    """Test initialization with custom config file path for OpenAI."""
    validator = AutogenValidator(backend="openai", config_path=temp_config_file_openai)
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "gpt-4o"
    assert config["temperature"] == 0.8
    assert config["max_tokens"] == 1500

def test_custom_config_path_ollama(temp_config_file_ollama):
    """Test initialization with custom config file path for Ollama."""
    validator = AutogenValidator(backend="ollama", config_path=temp_config_file_ollama)
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "llama3.2"
    assert config["temperature"] == 0.8
    assert config["num_predict"] == 1500

def test_env_overrides_config_openai(temp_env_file_openai, temp_config_file_openai):
    """Test that environment variables override config file values for OpenAI."""
    validator = AutogenValidator(
        backend="openai",
        env_path=temp_env_file_openai,
        config_path=temp_config_file_openai
    )
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "gpt-4o"  # From env
    assert config["max_tokens"] == 1500  # From env

def test_env_overrides_config_ollama(temp_env_file_ollama, temp_config_file_ollama):
    """Test that environment variables override config file values for Ollama."""
    validator = AutogenValidator(
        backend="ollama",
        env_path=temp_env_file_ollama,
        config_path=temp_config_file_ollama
    )
    assert validator.is_valid
    config = validator.config
    assert config["model"] == "llama3.2"  # From env
    assert config["num_predict"] == 1500  # From env

def test_invalid_values():
    """Test validation of invalid configuration values."""
    validator = AutogenValidator()

    # Test invalid temperature
    validator._config = {
        "model": "gpt-4o",
        "temperature": 3.0,  # Invalid: > 2.0
        "max_tokens": 1500
    }
    assert not validator.is_valid

    # Test invalid max_tokens
    validator._config = {
        "model": "gpt-4o",
        "temperature": 0.8,
        "max_tokens": -1  # Invalid: < 0
    }
    assert not validator.is_valid

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
    assert "Model: gpt-4o" in captured.out

def test_search_tree(tmp_path):
    """Test .env file search in directory tree."""
    # Create a nested directory structure with .env file
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    env_file = tmp_path / "a" / ".env"
    env_file.write_text("""
AUTOGEN_MODEL=gpt-4o
AUTOGEN_TEMPERATURE=0.8
AUTOGEN_MAX_TOKENS=1500
""".strip())

    # Change to the nested directory and initialize validator
    os.chdir(nested_dir)
    validator = AutogenValidator(backend="openai")
    assert validator.is_valid
    assert validator.config["model"] == "gpt-4o"