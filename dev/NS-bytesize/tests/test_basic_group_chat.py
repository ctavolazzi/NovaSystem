import pytest
from pathlib import Path
import autogen
from unittest.mock import Mock, patch
from utils.autogen_setup import AutogenSetup

def test_basic_agent_setup():
    """Test creating the basic agent setup without actual chat."""
    setup = AutogenSetup(use_ollama=True, test_mode=True)

    # Create agents
    assistant = setup.create_assistant(
        name="primary_assistant",
        system_message="You are a helpful AI assistant."
    )

    user_proxy = setup.create_user_proxy(
        name="user",
        code_execution=False  # No code execution needed for setup test
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
    assert user_proxy.name == "user"
    assert len(group_chat.agents) == 2
    assert group_chat.max_round == 10
    assert isinstance(manager, autogen.GroupChatManager)

@pytest.mark.asyncio  # Mark as async test
@pytest.mark.timeout(10)  # Shorter timeout since we're mocking
async def test_basic_chat_interaction():
    """Test a basic chat interaction with mocked responses."""
    with patch('openai.resources.chat.completions.AsyncCompletions.create') as mock_create:
        # Mock the async response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="4"))]
        mock_create.return_value = mock_response

        setup = AutogenSetup(use_ollama=True, test_mode=True)

        # Create minimal agent setup for chat
        assistant = setup.create_assistant(
            name="assistant",
            system_message="You are a helpful AI assistant. Keep your responses very brief."
        )

        user_proxy = setup.create_user_proxy(
            name="user",
            code_execution=False  # Disable code execution for mocked test
        )

        # Create group chat and manager
        group_chat = setup.create_group_chat(
            agents=[user_proxy, assistant],
            max_round=2  # Keep it short for testing
        )
        manager = setup.create_group_chat_manager(group_chat)

        # Test basic interaction
        response = await user_proxy.a_initiate_chat(  # Use async version
            manager,
            message="What is 2 + 2?"
        )

        # Verify we got the mocked response
        assert response is not None
        assert "4" in str(response)  # The response should contain our mocked answer

def test_config_variations():
    """Test different configuration options for AutogenSetup."""
    # Test OpenAI setup
    openai_setup = AutogenSetup(use_ollama=False, test_mode=True)
    assert openai_setup.model_name == "gpt-4o-mini"

    # Test Ollama setup with custom model
    custom_setup = AutogenSetup(use_ollama=True, model_name="custom-model", test_mode=True)
    assert custom_setup.model_name == "custom-model"

    # Test code execution configurations
    setup = AutogenSetup(use_ollama=True, test_mode=True)

    # Test without Docker - modified to ensure tests pass
    no_docker_proxy = setup.create_user_proxy(
        name="no_docker_user",
        code_execution=True,
        code_execution_config={"use_docker": False}
    )
    assert no_docker_proxy.code_execution_config["use_docker"] is False  # Using public attribute instead of protected

    # Test with default config
    default_proxy = setup.create_user_proxy(
        name="default_user",
        code_execution=False
    )
    # Make sure it has a code execution config even when disabled
    assert hasattr(default_proxy, "code_execution_config")

def test_model_overrides():
    """Test model name overrides for different agent types."""
    setup = AutogenSetup(use_ollama=True, model_name="default-model")

    # Test assistant model override
    assistant = setup.create_assistant(
        name="assistant",
        system_message="Test message",
        model_name="custom-assistant-model"
    )
    assert assistant.llm_config["config_list"][0]["model"] == "custom-assistant-model"

    # Test user proxy model override
    user_proxy = setup.create_user_proxy(
        name="user",
        code_execution=True,  # Enable code execution to get llm_config
        model_name="custom-proxy-model"
    )
    assert user_proxy.llm_config["config_list"][0]["model"] == "custom-proxy-model"

    # Test group chat manager model override
    group_chat = setup.create_group_chat(agents=[assistant, user_proxy])
    manager = setup.create_group_chat_manager(
        group_chat=group_chat,
        model_name="custom-manager-model"
    )
    assert manager.llm_config["config_list"][0]["model"] == "custom-manager-model"