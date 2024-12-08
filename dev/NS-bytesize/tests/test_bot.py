import pytest
from unittest.mock import Mock, AsyncMock, patch
from bots.bot import NovaBot, Agent
from hubs.hub import NovaHub

@pytest.fixture
def mock_hub():
    hub = Mock(spec=NovaHub)
    hub.generate_response = AsyncMock(return_value="Test response")
    return hub

@pytest.fixture
def nova_bot(mock_hub):
    return NovaBot(hub=mock_hub, name="TestBot", description="A test bot")

@pytest.mark.asyncio
async def test_bot_initialization(nova_bot):
    """Test bot initialization and properties"""
    assert nova_bot.name == "TestBot"
    assert nova_bot.description == "A test bot"
    assert nova_bot.session_id is None

    session_id = await nova_bot.initialize()
    assert nova_bot.session_id is not None
    assert isinstance(session_id, str)

@pytest.mark.asyncio
async def test_send_receive_message(nova_bot):
    """Test sending and receiving messages between agents"""
    # Create a mock recipient
    recipient = Mock(spec=Agent)
    recipient.a_receive = AsyncMock()

    # Test string message
    await nova_bot.a_send("Hello", recipient)
    recipient.a_receive.assert_called_once()
    call_args = recipient.a_receive.call_args[0]
    assert call_args[0]["role"] == "assistant"
    assert call_args[0]["content"] == "Hello"
    assert call_args[1] == nova_bot

    # Test dict message
    message = {"role": "assistant", "content": "Test"}
    recipient.a_receive.reset_mock()
    await nova_bot.a_send(message, recipient)
    recipient.a_receive.assert_called_once_with(message, nova_bot, None)

@pytest.mark.asyncio
async def test_generate_reply(nova_bot, mock_hub):
    """Test reply generation"""
    messages = [{"role": "user", "content": "Hello"}]

    # Test async reply generation
    reply = await nova_bot.a_generate_reply(messages)
    assert reply["role"] == "assistant"
    assert reply["content"] == "Test response"
    mock_hub.generate_response.assert_called_once()

    # Test with empty messages
    reply = await nova_bot.a_generate_reply(None)
    assert reply is None

@pytest.mark.asyncio
async def test_conversation_flow(nova_bot):
    """Test a complete conversation flow"""
    # Initialize the bot
    await nova_bot.initialize()

    # Create a mock sender
    sender = Mock(spec=Agent)
    sender.a_receive = AsyncMock()

    # Receive a message and generate reply
    message = {"role": "user", "content": "Hello"}
    await nova_bot.a_receive(message, sender, request_reply=True)

    # Verify message history
    assert len(nova_bot.message_history) == 2  # Original message + reply
    assert nova_bot.message_history[0]["role"] == "user"
    assert nova_bot.message_history[1]["role"] == "assistant"

@pytest.mark.asyncio
async def test_legacy_process_message(nova_bot, mock_hub):
    """Test the legacy process_message method"""
    response = await nova_bot.process_message("Hello", model="test-model")
    assert response == "Test response"
    mock_hub.generate_response.assert_called_once_with(
        prompt="Hello",
        system=nova_bot.system_prompt,
        model="test-model"
    )

@pytest.mark.asyncio
async def test_cleanup(nova_bot):
    """Test bot cleanup"""
    # Initialize and add some messages
    await nova_bot.initialize()
    await nova_bot.a_receive("Test message", Mock(spec=Agent))

    # Verify state before cleanup
    assert nova_bot.session_id is not None
    assert len(nova_bot.message_history) > 0

    # Cleanup
    await nova_bot.cleanup()

    # Verify cleaned state
    assert nova_bot.session_id is None
    assert len(nova_bot.message_history) == 0