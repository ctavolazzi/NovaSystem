import pytest
from unittest.mock import Mock, AsyncMock, patch
from io import StringIO
from agents.console_agent import ConsoleAgent
from bots.bot import Agent
from hubs.hub import NovaHub
import asyncio
import re

@pytest.fixture
def mock_hub():
    hub = Mock(spec=NovaHub)
    hub.generate_response = AsyncMock(return_value="Test response")
    return hub

@pytest.fixture
def console_agent(mock_hub):
    return ConsoleAgent(
        hub=mock_hub,
        name="TestAgent",
        description="A test agent",
        show_timestamp=False,  # Disable timestamp for predictable output
        debug=True,
        test_mode=True  # Enable test mode
    )

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_send_message(console_agent):
    """Test sending a message with console output"""
    recipient = Mock(spec=Agent)
    recipient.name = "RecipientAgent"
    recipient.a_receive = AsyncMock()

    with patch('sys.stdout', new=StringIO()) as fake_out:
        # Test sending string message
        await console_agent.a_send("Hello", recipient)
        output = fake_out.getvalue()

        # Verify console output
        assert "Sending message to RecipientAgent" in output
        assert "Message: Hello" in output
        assert "Message sent to RecipientAgent" in output

        # Verify the message was sent
        recipient.a_receive.assert_called_once()

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_receive_message(console_agent):
    """Test receiving a message with console output"""
    sender = Mock(spec=Agent)
    sender.name = "SenderAgent"

    with patch('sys.stdout', new=StringIO()) as fake_out:
        # Test receiving string message
        await console_agent.a_receive("Hello", sender)
        output = fake_out.getvalue()

        # Verify console output
        assert "Received message from SenderAgent" in output
        assert "Message: Hello" in output

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_generate_reply(console_agent):
    """Test generating a reply with console output"""
    messages = [{"content": "Test message"}]
    sender = Mock(spec=Agent)
    sender.name = "SenderAgent"

    # Create a mock for the superclass's a_generate_reply
    async def mock_generate_reply(*args, **kwargs):
        return "Test response"

    # Patch the superclass's method
    with patch('bots.bot.NovaBot.a_generate_reply', new=mock_generate_reply), \
         patch('sys.stdout', new=StringIO()) as fake_out:

        reply = await console_agent.a_generate_reply(messages, sender)
        output = fake_out.getvalue()

        # Strip ANSI codes for easier assertion
        clean_output = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', output)

        # Verify console output
        assert "Generating reply to SenderAgent" in clean_output
        assert "Reply generated" in clean_output
        assert reply == "Test response"  # From mock

@pytest.mark.asyncio
@pytest.mark.timeout(5)
async def test_cleanup(console_agent):
    """Test cleanup with console output"""
    with patch('sys.stdout', new=StringIO()) as fake_out:
        await console_agent.cleanup()
        output = fake_out.getvalue()

        # Verify console output
        assert "Cleaning up agent resources" in output
        assert "Cleanup complete" in output