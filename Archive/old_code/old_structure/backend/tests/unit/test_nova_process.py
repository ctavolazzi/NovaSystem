"""
Unit tests for the NovaProcessManager class.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import uuid
from datetime import datetime
import sys
import os

# Add the correct path to allow importing the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from nova_process import NovaProcessManager, ProcessStage


@pytest.fixture
def nova_process_manager():
    """Returns a NovaProcessManager instance for testing."""
    manager = NovaProcessManager()
    # Ensure the iterations dictionary is empty
    manager.iterations = {}
    return manager


@pytest.fixture
def mock_agent_factory():
    """Returns a mock agent factory for testing."""
    mock = MagicMock()

    # Create mock agents
    mock_dce = MagicMock()
    mock_dce.agent_type = "DCE"
    mock_dce.process_input.return_value = {
        "role": "assistant",
        "content": "This is a response from the DCE agent."
    }

    mock_cae = MagicMock()
    mock_cae.agent_type = "CAE"
    mock_cae.process_input.return_value = {
        "role": "assistant",
        "content": "This is a response from the CAE agent."
    }
    mock_cae.analyze_solution.return_value = {
        "weaknesses": ["Weakness 1"],
        "improvements": ["Improvement 1"],
        "blind_spots": ["Blind spot 1"]
    }

    mock_domain_expert = MagicMock()
    mock_domain_expert.agent_type = "DOMAIN_EXPERT"
    mock_domain_expert.process_input.return_value = {
        "role": "assistant",
        "content": "This is a response from the Domain Expert agent."
    }

    # Configure the mock factory to return appropriate agents
    def create_agent_side_effect(agent_type, **kwargs):
        if agent_type == "DCE":
            return mock_dce
        elif agent_type == "CAE":
            return mock_cae
        elif agent_type == "DOMAIN_EXPERT":
            return mock_domain_expert
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    mock.create_agent.side_effect = create_agent_side_effect
    return mock


def test_create_iteration(nova_process_manager):
    """Test the initialization of a new NovaProcessManager instance."""
    session_id = "test-session-id"
    problem_statement = "This is a test problem statement."

    # Check that the manager is properly initialized
    assert nova_process_manager.sessions == {}
    assert nova_process_manager.iterations == {}
    assert nova_process_manager.session_iterations == {}

    # Basic initialization test - doesn't test _create_iteration directly
    # since that's an implementation detail, not a public method
    assert isinstance(nova_process_manager, NovaProcessManager)


@pytest.mark.asyncio
@patch("nova_process.create_dce_agent")
async def test_start_iteration(mock_create_dce, nova_process_manager):
    """Test starting a new iteration."""
    # Setup mock
    mock_agent = AsyncMock()
    mock_agent.process.return_value = {"response": "Mocked analysis"}
    mock_create_dce.return_value = mock_agent

    session_id = "test-session-id"
    problem_statement = "This is a test problem statement."

    # Start an iteration
    iteration = await nova_process_manager.start_iteration(session_id, problem_statement)

    # Assertions
    assert iteration is not None
    assert iteration["id"] is not None
    iteration_id = iteration["id"]
    assert iteration["problem_statement"] == problem_statement
    assert iteration["session_id"] == session_id
    assert iteration["complete"] is False
    assert ProcessStage.PROBLEM_UNPACKING.value in iteration["stages"]

    # Verify the iteration was stored
    assert iteration_id in nova_process_manager.iterations


@pytest.mark.asyncio
@patch("nova_process.create_dce_agent")
async def test_get_iteration(mock_create_dce, nova_process_manager):
    """Test retrieving an iteration by ID."""
    # Setup mock
    mock_agent = AsyncMock()
    mock_agent.process.return_value = {"response": "Mocked analysis"}
    mock_create_dce.return_value = mock_agent

    # Create an iteration
    session_id = "test-session-id"
    problem_statement = "This is a test problem statement."
    iteration = await nova_process_manager.start_iteration(session_id, problem_statement)
    iteration_id = iteration["id"]

    # Get the iteration
    retrieved_iteration = await nova_process_manager.get_iteration(session_id, iteration_id)

    # Assertions
    assert retrieved_iteration is not None
    assert retrieved_iteration["id"] == iteration_id
    assert retrieved_iteration["problem_statement"] == problem_statement

    # Test retrieving a non-existent iteration
    assert await nova_process_manager.get_iteration(session_id, "non-existent-id") is None
    assert await nova_process_manager.get_iteration("non-existent-session", iteration_id) is None


@pytest.mark.asyncio
@patch("nova_process.create_dce_agent")
async def test_list_iterations(mock_create_dce, nova_process_manager):
    """Test listing iterations for a session."""
    # Setup mock
    mock_agent = AsyncMock()
    mock_agent.process.return_value = {"response": "Mocked analysis"}
    mock_create_dce.return_value = mock_agent

    # Create iterations
    session_id = "test-session-id"
    await nova_process_manager.start_iteration(session_id, "Problem 1")
    await nova_process_manager.start_iteration(session_id, "Problem 2")

    # List iterations
    iterations = nova_process_manager.list_iterations(session_id)

    # Assertions
    assert iterations is not None
    assert len(iterations) == 2

    # Test listing iterations for a non-existent session
    non_existent_iterations = nova_process_manager.list_iterations("non-existent-session")
    assert non_existent_iterations is not None
    assert len(non_existent_iterations) == 0


@pytest.mark.asyncio
@patch("nova_process.create_dce_agent")
async def test_execute_problem_unpacking_stage(mock_create_dce, nova_process_manager):
    """Test executing the problem unpacking stage."""
    # Setup mock
    mock_agent = AsyncMock()
    mock_agent.process.return_value = {"response": "Mocked response"}
    mock_create_dce.return_value = mock_agent

    # Create an iteration
    session_id = "test-session-id"
    problem_statement = "This is a test problem."

    # Start an iteration which will execute the problem unpacking stage
    iteration = await nova_process_manager.start_iteration(session_id, problem_statement)
    iteration_id = iteration["id"]

    # Get the result of the stage execution
    result = iteration["stages"][ProcessStage.PROBLEM_UNPACKING.value]

    # Assertions
    assert result is not None
    assert "result" in result
    assert result["result"] == "Mocked response"
    mock_agent.process.assert_called_once()


@pytest.mark.asyncio
@patch("nova_process.create_dce_agent")
async def test_continue_iteration(mock_create_dce, nova_process_manager):
    """Test continuing an iteration to the next stage."""
    # Setup mock
    mock_agent = AsyncMock()
    mock_agent.process.return_value = {"response": "Mocked analysis"}
    mock_create_dce.return_value = mock_agent

    # Create an iteration
    session_id = "test-session-id"
    problem_statement = "This is a test problem."

    # Start an iteration (which executes problem_unpacking stage)
    iteration = await nova_process_manager.start_iteration(session_id, problem_statement)
    iteration_id = iteration["id"]

    # Continue to the next stage
    updated_iteration = await nova_process_manager.continue_iteration(session_id, iteration_id)

    # Assertions
    assert updated_iteration is not None
    assert ProcessStage.EXPERTISE_ASSEMBLY.value in updated_iteration["stages"]