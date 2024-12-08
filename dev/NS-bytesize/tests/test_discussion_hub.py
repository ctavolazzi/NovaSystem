import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from hubs.discussion_hub import DiscussionHub
from utils.autogen_setup import AutogenSetup

@pytest.fixture
def discussion_hub():
    # Create hub with test mode enabled
    hub = DiscussionHub()
    hub.setup = AutogenSetup(test_mode=True)
    return hub

@pytest.mark.asyncio
@pytest.mark.timeout(10)  # Shorter timeout for tests
async def test_start_discussion(discussion_hub):
    """Test starting a new discussion."""
    # Start a discussion
    discussion_id = await discussion_hub.start_discussion("Test topic")

    # Verify discussion was created
    assert discussion_id in discussion_hub.active_discussions
    assert discussion_hub.active_discussions[discussion_id]["topic"] == "Test topic"

    # Verify agents were created
    agents = discussion_hub.active_discussions[discussion_id]["agents"]
    assert "controller" in agents
    assert "analyst" in agents
    assert "synthesizer" in agents
    assert "implementer" in agents
    assert "user_proxy" in agents

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_add_message_to_discussion(discussion_hub):
    """Test adding a message to an ongoing discussion."""
    # Start a discussion first
    discussion_id = await discussion_hub.start_discussion("Test topic")

    # Add a message
    response = await discussion_hub.add_message_to_discussion(
        discussion_id,
        "Test message"
    )

    # Verify response
    assert response == "Test response"

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_end_discussion(discussion_hub):
    """Test ending a discussion."""
    # Start a discussion
    discussion_id = await discussion_hub.start_discussion("Test topic")

    # End the discussion
    summary = await discussion_hub.end_discussion(discussion_id)

    # Verify discussion was ended and removed
    assert discussion_id not in discussion_hub.active_discussions
    assert summary == "Test response"

@pytest.mark.asyncio
async def test_invalid_discussion_id(discussion_hub):
    """Test handling invalid discussion IDs."""
    with pytest.raises(ValueError):
        await discussion_hub.add_message_to_discussion(
            "invalid_id",
            "Test message"
        )

    with pytest.raises(ValueError):
        await discussion_hub.end_discussion("invalid_id")