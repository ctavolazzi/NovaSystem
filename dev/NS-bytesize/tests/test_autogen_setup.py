import pytest
from pathlib import Path
import json
from unittest.mock import patch, MagicMock
import autogen

from utils.autogen_setup import AutogenSetup

@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file for testing."""
    config_file = tmp_path / "config.json"
    config = {
        "model": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 2000,
        "seed": 123,
        "api_key": "dummy-api-key"  # Added for OpenAI config
    }
    config_file.write_text(json.dumps(config))
    return config_file

@pytest.fixture
def mock_env_with_api_key(monkeypatch):
    """Mock environment with API key."""
    monkeypatch.setenv("OPENAI_API_KEY", "dummy-api-key")

@pytest.fixture
def mock_autogen_config(temp_config_file, mock_env_with_api_key):
    """Create a mock configuration for testing."""
    return temp_config_file

def test_openai_initialization_with_model(mock_autogen_config):
    """Test initialization with OpenAI configuration and specific model."""
    setup = AutogenSetup(config_path=mock_autogen_config, use_ollama=False, model_name="gpt-4o")
    assert setup._config["model"] == "gpt-4o"
    assert setup._config["api_key"] == "dummy-api-key"
    assert setup._config["temperature"] == 0.7
    assert setup._config["max_tokens"] == 2000

def test_ollama_initialization_with_model(mock_autogen_config):
    """Test initialization with Ollama configuration and specific model."""
    setup = AutogenSetup(config_path=mock_autogen_config, use_ollama=True, model_name="llama3")
    assert setup._config["model"] == "llama3"
    assert setup._config["base_url"] == "http://localhost:11434/v1"
    assert setup._config["api_key"] == "ollama"
    assert setup._config["temperature"] == 0.7
    assert setup._config["max_tokens"] == 2000

@patch('autogen.AssistantAgent')
def test_create_assistant_with_model(mock_assistant):
    """Test creating an assistant agent with a specific model."""
    setup = AutogenSetup(use_ollama=True, model_name="llama3")
    assistant = setup.create_assistant(
        name="test_assistant",
        system_message="You are a helpful assistant.",
        model_name="llama3"
    )
    mock_assistant.assert_called_once()
    config = mock_assistant.call_args[1]["llm_config"]["config_list"][0]
    assert config["model"] == "llama3"
    assert config["base_url"] == "http://localhost:11434/v1"

@patch('autogen.UserProxyAgent')
def test_create_user_proxy_with_model(mock_user_proxy):
    """Test creating a user proxy agent with a specific model."""
    setup = AutogenSetup(use_ollama=True, model_name="llama3")
    user_proxy = setup.create_user_proxy(
        name="test_user",
        code_execution=True,
        model_name="llama3"
    )
    mock_user_proxy.assert_called_once()
    config = mock_user_proxy.call_args[1]["llm_config"]["config_list"][0]
    assert config["model"] == "llama3"
    assert config["base_url"] == "http://localhost:11434/v1"

@patch('autogen.AssistantAgent')
@patch('autogen.UserProxyAgent')
@patch('autogen.GroupChat')
def test_create_group_chat(mock_group_chat, mock_user_proxy, mock_assistant):
    """Test creating a group chat."""
    setup = AutogenSetup(use_ollama=True, model_name="llama3")
    assistant = setup.create_assistant("assistant", "You are helpful.")
    user_proxy = setup.create_user_proxy("user")
    group_chat = setup.create_group_chat([assistant, user_proxy])
    mock_group_chat.assert_called_once()
    assert mock_group_chat.call_args[1]["max_round"] == 12

@patch('autogen.AssistantAgent')
@patch('autogen.UserProxyAgent')
@patch('autogen.GroupChat')
@patch('autogen.GroupChatManager')
def test_create_group_chat_manager_with_model(
    mock_manager, mock_group_chat, mock_user_proxy, mock_assistant
):
    """Test creating a group chat manager with a specific model."""
    setup = AutogenSetup(use_ollama=True, model_name="llama3")
    assistant = setup.create_assistant("assistant", "You are helpful.")
    user_proxy = setup.create_user_proxy("user")
    group_chat = setup.create_group_chat([assistant, user_proxy])
    manager = setup.create_group_chat_manager(group_chat, model_name="llama3")
    mock_manager.assert_called_once()
    config = mock_manager.call_args[1]["llm_config"]["config_list"][0]
    assert config["model"] == "llama3"
    assert config["base_url"] == "http://localhost:11434/v1"

def test_basic_agent_setup():
    """Test creating the basic agent setup without actual chat."""
    setup = AutogenSetup(use_ollama=True, test_mode=True)

    # Create agents with descriptions
    assistant = setup.create_assistant(
        name="primary_assistant",
        system_message="You are a helpful AI assistant.",
        description="A primary AI assistant for general tasks"
    )

    user_proxy = setup.create_user_proxy(
        name="user",
        code_execution=False,  # No code execution needed for setup test
        description="A user proxy for testing"
    )

    # Create group chat
    group_chat = setup.create_group_chat(
        agents=[user_proxy, assistant],
        max_round=10
    )

    # Create manager
    manager = setup.create_group_chat_manager(group_chat)

    # Verify the setup
    assert assistant.name == "primary_assistant"
    assert assistant.description == "A primary AI assistant for general tasks"
    assert user_proxy.name == "user"
    assert user_proxy.description == "A user proxy for testing"
    assert len(group_chat.agents) == 2
    assert group_chat.max_round == 10
    assert isinstance(manager, autogen.GroupChatManager)

def test_default_descriptions():
    """Test default descriptions for agents."""
    setup = AutogenSetup(use_ollama=True)

    assistant = setup.create_assistant(
        name="test_assistant",
        system_message="Test message"
    )
    assert assistant.description == "An AI assistant named test_assistant"

    user_proxy = setup.create_user_proxy(name="test_user")
    assert user_proxy.description == "A user proxy agent named test_user"

def test_system_message_update():
    """Test updating system messages for agents."""
    setup = AutogenSetup(use_ollama=True)

    assistant = setup.create_assistant(
        name="test_assistant",
        system_message="Initial message"
    )

    # Update system message
    new_message = "Updated system message"
    setup.update_agent_system_message(assistant, new_message)
    assert assistant.system_message == new_message

    # For user proxy, we don't expect an attribute error anymore
    # The mock implementation in test mode handles system message updates
    user_proxy = setup.create_user_proxy(name="test_user")
    setup.update_agent_system_message(user_proxy, "New message")

def test_model_overrides():
    """Test model name overrides for different agent types."""
    setup = AutogenSetup(use_ollama=True, model_name="default-model")

    # Test assistant model override with description
    assistant = setup.create_assistant(
        name="assistant",
        system_message="Test message",
        model_name="custom-assistant-model",
        description="Custom assistant description"
    )
    assert assistant.llm_config["config_list"][0]["model"] == "custom-assistant-model"
    assert assistant.description == "Custom assistant description"

    # Test user proxy model override with description
    user_proxy = setup.create_user_proxy(
        name="user",
        code_execution=True,  # Enable code execution to get llm_config
        model_name="custom-proxy-model",
        description="Custom proxy description"
    )
    assert user_proxy.llm_config["config_list"][0]["model"] == "custom-proxy-model"
    assert user_proxy.description == "Custom proxy description"

    # Test group chat manager model override
    group_chat = setup.create_group_chat(agents=[assistant, user_proxy])
    manager = setup.create_group_chat_manager(
        group_chat=group_chat,
        model_name="custom-manager-model"
    )
    assert manager.llm_config["config_list"][0]["model"] == "custom-manager-model"
