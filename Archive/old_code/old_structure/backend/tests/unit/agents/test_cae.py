"""
Unit tests for the Critical Analysis Expert (CAE) agent.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add the correct path to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../')))

# Import using relative paths
from backend.agents.cae import CAEAgent


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
    mock.generate_text = MagicMock(return_value="""
I've critically analyzed the proposed solution. Here's my assessment:

## Strengths
1. Simple and straightforward approach
2. Easy to implement quickly

## Weaknesses
1. Scalability issues with the current architecture
2. Security vulnerabilities in the authentication system
3. Lack of proper error handling

## Improvements
1. Implement a distributed architecture for better scalability
2. Add multi-factor authentication and JWT token validation
3. Develop a comprehensive error handling strategy with proper logging

## Overall Assessment
The solution has merit for its simplicity but requires significant improvements in
security, scalability, and error handling before it can be considered robust.
    """)
    return mock


@pytest.fixture
def cae_agent(mock_llm_provider):
    """Returns a CAE agent instance for testing."""
    # Create agent with mocked provider
    return CAEAgent(config={
        "provider_class": type(mock_llm_provider),
        "provider": mock_llm_provider  # Keep this for backward compatibility
    })


def test_cae_agent_initialization():
    """Test the initialization of the CAE agent."""
    # Create a mock provider
    mock_provider = MagicMock()

    # Create the agent
    agent = CAEAgent(config={"provider": mock_provider})

    # Assertions
    assert agent is not None
    assert agent.name == "CAE"
    assert agent.role == "Critical Analysis Expert"
    assert "critical analysis" in agent.system_prompt.lower()


@pytest.mark.asyncio
@patch("backend.agents.cae.CAEAgent._build_prompt")
@patch("backend.agents.cae.CAEAgent._parse_analysis")
async def test_cae_agent_process(mock_parse, mock_build, cae_agent, mock_llm_provider):
    """Test the process method of the CAE agent."""
    # Setup mocks
    mock_build.return_value = "Test prompt"
    mock_parse.return_value = {
        "strengths": ["Strength 1"],
        "weaknesses": ["Weakness 1"],
        "improvements": ["Improvement 1"],
        "overall_assessment": "Good but needs work"
    }

    # Test data
    input_data = {
        "message": "Analyze this solution",
        "context": {"key": "value"},
        "proposed_solution": "This is a proposed solution"
    }

    # Call process method
    result = await cae_agent.process(input_data)

    # Assertions
    assert result is not None
    assert "response" in result
    assert "analysis" in result
    assert result["analysis"] == mock_parse.return_value

    # Verify mock calls
    mock_build.assert_called_once()
    mock_llm_provider.complete.assert_called_once()
    mock_parse.assert_called_once()


def test_parse_analysis(cae_agent):
    """Test the _parse_analysis method."""
    # Test data
    response = """
## Strengths
- Strong feature set
- Good performance

## Weaknesses
- Security issues
- Scalability concerns

## Improvements
- Add authentication
- Use distributed architecture

## Overall Assessment
Needs work but promising.
    """

    # Call parse method
    result = cae_agent._parse_analysis(response)

    # Assertions
    assert result is not None
    assert "strengths" in result
    assert "weaknesses" in result
    assert "improvements" in result
    assert "overall_assessment" in result

    assert len(result["strengths"]) == 2
    assert "Strong feature set" in result["strengths"]

    assert len(result["weaknesses"]) == 2
    assert "Security issues" in result["weaknesses"]

    assert len(result["improvements"]) == 2
    assert "Add authentication" in result["improvements"]

    assert "Needs work but promising" in result["overall_assessment"]