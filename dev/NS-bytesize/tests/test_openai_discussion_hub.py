import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from hubs.openai_discussion_hub import OpenAIDiscussionHub, DiscussionConfig
import openai
from dotenv import load_dotenv

# Load the root .env file
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

@pytest.fixture
async def mock_autogen():
    """Mock all necessary autogen components with proper async support"""
    with patch('autogen.OpenAIWrapper') as mock_wrapper, \
         patch('autogen.AssistantAgent') as mock_assistant, \
         patch('autogen.UserProxyAgent') as mock_proxy, \
         patch('autogen.GroupChat') as mock_group:

        # Mock OpenAI responses
        mock_wrapper.return_value = MagicMock()
        mock_wrapper.return_value.create = AsyncMock(return_value=MagicMock(
            choices=[MagicMock(message=MagicMock(content="Test response"))]
        ))

        # Mock agents
        mock_assistant.return_value = MagicMock()
        mock_assistant.return_value.name = "Test Assistant"
        mock_assistant.return_value.system_message = "Test system message"
        mock_assistant.return_value.initiate_chat = AsyncMock(return_value="Test response")

        # Mock user proxy
        mock_chat_response = MagicMock()
        mock_chat_response.summary = "Test response"
        mock_proxy.return_value = MagicMock()
        mock_proxy.return_value.initiate_chat = AsyncMock(return_value=mock_chat_response)

        # Mock group chat
        mock_group.return_value = MagicMock()
        mock_group.return_value.agents = [mock_assistant.return_value] * 5
        mock_group.return_value.max_round = 10
        mock_group.return_value.speaker_selection_method = "round_robin"
        mock_group.return_value.allow_repeat_speaker = False

        yield {
            'wrapper': mock_wrapper,
            'assistant': mock_assistant,
            'proxy': mock_proxy,
            'group': mock_group
        }

@pytest.fixture
async def hub(mock_autogen):
    """Create a hub instance with test configuration"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        pytest.skip("OPENAI_API_KEY not found in environment")
    return OpenAIDiscussionHub(api_key=api_key)

@pytest.fixture
async def error_hub():
    """Create a hub instance for error testing"""
    return OpenAIDiscussionHub(api_key="test-key")

class TestDiscussionHubErrors:
    """Test error handling in the OpenAI Discussion Hub"""

    @pytest.mark.asyncio
    async def test_invalid_discussion_id(self, error_hub):
        """Test handling of invalid discussion ID"""
        with pytest.raises(ValueError, match="Discussion .* not found"):
            await error_hub.add_message_to_discussion("invalid-id", "test message")

    @pytest.mark.asyncio
    async def test_agent_creation_failure(self, error_hub):
        """Test handling of agent creation failures"""
        with patch('autogen.AssistantAgent', side_effect=Exception("Agent creation failed")):
            with pytest.raises(Exception) as exc_info:
                error_hub.create_discussion_agents("test-id")
            assert "Agent creation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_message_addition_failure(self, error_hub, mock_autogen):
        """Test handling of message addition failures"""
        discussion_id = await error_hub.start_discussion("Test topic")
        mock_autogen['proxy'].return_value.initiate_chat = AsyncMock(side_effect=Exception("Message failed"))

        with pytest.raises(Exception) as exc_info:
            await error_hub.add_message_to_discussion(discussion_id, "test message")
        assert "Message failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_start_discussion_failure(self, error_hub, mock_autogen):
        """Test handling of discussion start failures"""
        mock_autogen['proxy'].return_value.initiate_chat = MagicMock(side_effect=Exception("Start failed"))

        with pytest.raises(Exception) as exc_info:
            await error_hub.start_discussion("Test topic")
        assert "Start failed" in str(exc_info.value)

class TestDiscussionHubConfig:
    """Test configuration handling in the OpenAI Discussion Hub"""

    @pytest.mark.asyncio
    async def test_custom_config(self, mock_autogen):
        """Test hub initialization with custom config"""
        custom_config = DiscussionConfig(
            max_rounds=5,
            temperature=0.5,
            max_tokens=1000,
            model="gpt-4-turbo"
        )

        # Mock the GroupChat to return our custom max_rounds
        mock_autogen['group'].return_value.max_round = custom_config.max_rounds

        hub = OpenAIDiscussionHub(api_key="test-key")
        agents = hub.create_discussion_agents("test-id")
        group_chat = hub.create_discussion_group(agents, max_rounds=custom_config.max_rounds)

        assert group_chat.max_round == custom_config.max_rounds
        assert len(group_chat.agents) == 5

    @pytest.mark.asyncio
    async def test_discussion_with_custom_config(self, mock_autogen):
        """Test starting a discussion with custom configuration"""
        custom_config = DiscussionConfig(
            max_rounds=5,
            temperature=0.5,
            max_tokens=1000,
            model="gpt-4-turbo"
        )

        hub = OpenAIDiscussionHub(api_key="test-key")
        discussion_id = await hub.start_discussion("Test topic", config=custom_config)

        discussion = hub.active_discussions[discussion_id]
        assert discussion["config"].max_rounds == custom_config.max_rounds
        assert discussion["config"].temperature == custom_config.temperature
        assert discussion["config"].max_tokens == custom_config.max_tokens
        assert discussion["config"].model == custom_config.model

    @pytest.mark.asyncio
    async def test_default_config(self, mock_autogen):
        """Test default configuration values"""
        hub = OpenAIDiscussionHub(api_key="test-key")
        discussion_id = await hub.start_discussion("Test topic")

        discussion = hub.active_discussions[discussion_id]
        assert discussion["config"].max_rounds == 10
        assert discussion["config"].temperature == 0.7
        assert discussion["config"].max_tokens == 2000
        assert discussion["config"].model == "gpt-4"

class TestDiscussionFlow:
    """Test the discussion flow and message handling"""

    @pytest.mark.asyncio
    async def test_message_formatting(self, hub):
        """Test proper formatting of discussion messages"""
        initial_message = hub._format_initial_message("Test topic")
        assert "Let's discuss: Test topic" in initial_message
        assert "Guidelines" in initial_message
        assert "Controller:" in initial_message

    @pytest.mark.asyncio
    async def test_discussion_lifecycle(self, hub, mock_autogen):
        """Test complete discussion lifecycle"""
        # Start discussion
        discussion_id = await hub.start_discussion("Test topic")
        assert discussion_id in hub.active_discussions

        # Add messages
        response1 = await hub.add_message_to_discussion(discussion_id, "First message")
        assert response1 is not None
        assert "Test response" in str(response1)

        response2 = await hub.add_message_to_discussion(discussion_id, "Second message")
        assert response2 is not None
        assert "Test response" in str(response2)

        # End discussion
        final_response = await hub.end_discussion(discussion_id)
        assert final_response is not None
        assert "Test response" in str(final_response)
        assert discussion_id not in hub.active_discussions

    @pytest.mark.asyncio
    async def test_concurrent_discussions(self, hub, mock_autogen):
        """Test handling multiple discussions concurrently"""
        # Start multiple discussions
        discussion_id1 = await hub.start_discussion("Topic 1")
        discussion_id2 = await hub.start_discussion("Topic 2")

        # Verify both discussions are active
        assert discussion_id1 in hub.active_discussions
        assert discussion_id2 in hub.active_discussions

        # Add messages to both discussions
        response1 = await hub.add_message_to_discussion(discussion_id1, "Message 1")
        response2 = await hub.add_message_to_discussion(discussion_id2, "Message 2")

        assert response1 is not None
        assert response2 is not None

        # End discussions
        await hub.end_discussion(discussion_id1)
        await hub.end_discussion(discussion_id2)

        assert discussion_id1 not in hub.active_discussions
        assert discussion_id2 not in hub.active_discussions

# Basic functionality tests
@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_create_discussion_agents(hub, mock_autogen):
    agents = hub.create_discussion_agents("test-discussion")
    assert "controller" in agents
    assert "analyst" in agents
    assert "architect" in agents
    assert "implementer" in agents
    assert "user_proxy" in agents

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_create_discussion_group(hub, mock_autogen):
    agents = hub.create_discussion_agents("test-discussion")
    group_chat = hub.create_discussion_group(agents)
    assert len(group_chat.agents) == 5
    assert group_chat.max_round == 10
    assert group_chat.speaker_selection_method == "round_robin"
    assert group_chat.allow_repeat_speaker is False

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_start_discussion(hub, mock_autogen):
    discussion_id = await hub.start_discussion("Test topic")
    assert isinstance(discussion_id, str)
    assert len(discussion_id) > 0

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_add_message_to_discussion(hub, mock_autogen):
    discussion_id = await hub.start_discussion("Test topic")
    response = await hub.add_message_to_discussion(discussion_id, "Test message")
    assert response is not None
    assert "Test response" in str(response)

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_end_discussion(hub, mock_autogen):
    discussion_id = await hub.start_discussion("Test topic")
    response = await hub.end_discussion(discussion_id)
    assert response is not None
    assert "Test response" in str(response)
    assert discussion_id not in hub.active_discussions