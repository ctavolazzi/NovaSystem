"""
Unit tests for the Discussion Continuity Expert (DCE) agent.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add the correct path to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import using relative paths
from backend.agents.dce import DCEAgent


@pytest.fixture
def mock_llm_provider():
    """Returns a mock LLM provider for testing."""
    mock = MagicMock()
    mock.complete = AsyncMock(return_value={
        "choices": [{
            "message": {
                "content": "Test LLM response"
            }
        }]
    })
    mock.complete_stream = AsyncMock()
    return mock


@pytest.fixture
def dce_agent(mock_llm_provider):
    """Returns a DCE agent instance for testing."""
    # Create agent with mocked provider
    return DCEAgent(config={
        "provider_class": type(mock_llm_provider),
        "provider": mock_llm_provider  # Keep this for backward compatibility
    })


def test_dce_agent_initialization():
    """Test the initialization of the DCE agent."""
    # Create a mock provider
    mock_provider = MagicMock()

    # Create the agent
    agent = DCEAgent(config={"provider": mock_provider})

    # Assertions
    assert agent is not None
    assert agent.name == "DCE"
    assert agent.role == "Discussion Continuity Expert"
    assert "discussion continuity" in agent.system_prompt.lower() or "dce" in agent.system_prompt.lower()


@pytest.mark.asyncio
async def test_dce_agent_process(dce_agent, mock_llm_provider):
    """Test the process method of the DCE agent."""
    # Test data
    input_data = {
        "message": "Hello, how can you help me?",
        "context": {"key": "value"}
    }

    # Call process method
    result = await dce_agent.process(input_data)

    # Assertions
    assert result is not None
    assert "response" in result
    assert result["response"] == "Test LLM response"

    # Verify mock calls
    mock_llm_provider.complete.assert_called_once()


@pytest.mark.asyncio
async def test_dce_agent_reset(dce_agent, mock_llm_provider):
    """Test resetting the conversation history."""
    # Add some conversation history
    await dce_agent.process({"message": "First message"})

    # Check that history exists
    assert len(dce_agent.conversation_history) > 0

    # Reset the conversation
    await dce_agent.process({"message": "New conversation", "reset": True})

    # In the current implementation, after reset the history should contain:
    # 1. The user message
    # 2. The assistant response from the mock provider
    assert len(dce_agent.conversation_history) == 2
    assert dce_agent.conversation_history[0]["role"] == "user"
    assert dce_agent.conversation_history[0]["content"] == "New conversation"
    assert dce_agent.conversation_history[1]["role"] == "assistant"
    assert dce_agent.conversation_history[1]["content"] == "Test LLM response"
