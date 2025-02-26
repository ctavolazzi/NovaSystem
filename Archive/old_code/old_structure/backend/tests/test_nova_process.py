"""
Unit tests for the Nova Process.
"""
import pytest
import asyncio
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
from nova_process import NovaProcessManager, ProcessStage

# Helper function to create a mock response from an agent
def create_agent_response(response_text):
    """Create a mock agent response."""
    return {"response": response_text}

class TestNovaProcessManager:
    """Test cases for the NovaProcessManager."""

    @pytest.fixture
    def manager(self):
        """Create a NovaProcessManager instance for testing."""
        return NovaProcessManager()

    @pytest.mark.asyncio
    @patch("nova_process.create_dce_agent")
    async def test_problem_unpacking_stage(self, mock_create_dce_agent, manager):
        """Test the problem unpacking stage."""
        # Set up the mock
        mock_dce = AsyncMock()
        mock_dce.process.return_value = create_agent_response("This is a problem analysis")
        mock_create_dce_agent.return_value = mock_dce

        # Create a test iteration
        session_id = str(uuid.uuid4())
        problem_statement = "Test problem statement"
        iteration = await manager.start_iteration(session_id, problem_statement)

        # Verify the stage was executed
        assert ProcessStage.PROBLEM_UNPACKING.value in iteration["stages"]
        assert "result" in iteration["stages"][ProcessStage.PROBLEM_UNPACKING.value]
        assert iteration["stages"][ProcessStage.PROBLEM_UNPACKING.value]["result"] == "This is a problem analysis"

        # Verify the agent was called with the right parameters
        mock_dce.process.assert_called_once()
        call_args = mock_dce.process.call_args[0][0]
        assert "message" in call_args
        assert problem_statement in call_args["message"]

    @pytest.mark.asyncio
    @patch("nova_process.create_dce_agent")
    async def test_expertise_assembly_stage(self, mock_create_dce_agent, manager):
        """Test the expertise assembly stage."""
        # Set up the DCE mock
        mock_dce = AsyncMock()
        mock_dce.process.return_value = create_agent_response("Required experts:\n- Marketing\n- UX Design\n- Customer Support")
        mock_create_dce_agent.return_value = mock_dce

        # Create a test iteration and move to expertise assembly
        session_id = str(uuid.uuid4())
        problem_statement = "Test problem statement"

        # First set up problem unpacking stage result
        iteration_id = str(uuid.uuid4())
        iteration = {
            "id": iteration_id,
            "session_id": session_id,
            "number": 1,
            "problem_statement": problem_statement,
            "start_time": "2023-01-01T00:00:00",
            "stages": {
                ProcessStage.PROBLEM_UNPACKING.value: {
                    "completed_at": "2023-01-01T00:01:00",
                    "result": "Problem analysis text"
                }
            },
            "required_experts": [],
            "expertise_contributions": {},
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }
        manager.iterations[iteration_id] = iteration
        manager.session_iterations[session_id] = [iteration_id]

        # Continue to expertise assembly
        iteration = await manager.continue_iteration(session_id, iteration_id)

        # Verify the stage was executed
        assert ProcessStage.EXPERTISE_ASSEMBLY.value in iteration["stages"]
        assert "result" in iteration["stages"][ProcessStage.EXPERTISE_ASSEMBLY.value]

        # Verify experts were extracted
        assert "Marketing" in iteration["required_experts"]
        assert "UX Design" in iteration["required_experts"]
        assert "Customer Support" in iteration["required_experts"]

    @pytest.mark.asyncio
    @patch("nova_process.create_dce_agent")
    @patch("nova_process.create_domain_expert_agent")
    async def test_collaborative_ideation_stage(self, mock_create_expert, mock_create_dce, manager):
        """Test the collaborative ideation stage."""
        # Set up the DCE mock
        mock_dce = AsyncMock()
        mock_dce.process.return_value = create_agent_response("DCE response")
        mock_create_dce.return_value = mock_dce

        # Set up the expert mock
        mock_expert = AsyncMock()
        mock_expert.process.return_value = create_agent_response("Expert response")
        mock_create_expert.return_value = mock_expert

        # Create a test iteration with expertise assembly completed
        session_id = str(uuid.uuid4())
        iteration_id = str(uuid.uuid4())
        iteration = {
            "id": iteration_id,
            "session_id": session_id,
            "number": 1,
            "problem_statement": "Test problem statement",
            "start_time": "2023-01-01T00:00:00",
            "stages": {
                ProcessStage.PROBLEM_UNPACKING.value: {
                    "completed_at": "2023-01-01T00:01:00",
                    "result": "Problem analysis text"
                },
                ProcessStage.EXPERTISE_ASSEMBLY.value: {
                    "completed_at": "2023-01-01T00:02:00",
                    "result": "Expertise assembly result"
                }
            },
            "required_experts": ["Marketing", "UX Design"],
            "expertise_contributions": {},
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }
        manager.iterations[iteration_id] = iteration
        manager.session_iterations[session_id] = [iteration_id]

        # Continue to collaborative ideation
        iteration = await manager.continue_iteration(session_id, iteration_id)

        # Verify the stage was executed
        assert ProcessStage.COLLABORATIVE_IDEATION.value in iteration["stages"]

        # Verify contributions from each expert
        assert "Marketing" in iteration["expertise_contributions"]
        assert "UX Design" in iteration["expertise_contributions"]
        assert "Discussion Continuity Expert" in iteration["expertise_contributions"]

    @pytest.mark.asyncio
    @patch("nova_process.create_cae_agent")
    async def test_critical_analysis_stage(self, mock_create_cae, manager):
        """Test the critical analysis stage."""
        # Set up the CAE mock
        mock_cae = AsyncMock()
        mock_cae.process.return_value = create_agent_response("Critical analysis result")
        mock_create_cae.return_value = mock_cae

        # Create a test iteration with collaborative ideation completed
        session_id = str(uuid.uuid4())
        iteration_id = str(uuid.uuid4())
        iteration = {
            "id": iteration_id,
            "session_id": session_id,
            "number": 1,
            "problem_statement": "Test problem statement",
            "start_time": "2023-01-01T00:00:00",
            "stages": {
                ProcessStage.PROBLEM_UNPACKING.value: {
                    "completed_at": "2023-01-01T00:01:00",
                    "result": "Problem analysis text"
                },
                ProcessStage.EXPERTISE_ASSEMBLY.value: {
                    "completed_at": "2023-01-01T00:02:00",
                    "result": "Expertise assembly result"
                },
                ProcessStage.COLLABORATIVE_IDEATION.value: {
                    "completed_at": "2023-01-01T00:03:00",
                    "result": {"Expert1": "Contribution 1", "Expert2": "Contribution 2"}
                }
            },
            "required_experts": ["Expert1", "Expert2"],
            "expertise_contributions": {
                "Expert1": "Contribution 1",
                "Expert2": "Contribution 2"
            },
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }
        manager.iterations[iteration_id] = iteration
        manager.session_iterations[session_id] = [iteration_id]

        # Continue to critical analysis
        iteration = await manager.continue_iteration(session_id, iteration_id)

        # Verify the stage was executed
        assert ProcessStage.CRITICAL_ANALYSIS.value in iteration["stages"]
        assert iteration["critical_analysis"] == "Critical analysis result"

    @pytest.mark.asyncio
    @patch("nova_process.create_dce_agent")
    async def test_summary_and_next_steps_stage(self, mock_create_dce, manager):
        """Test the summary and next steps stage."""
        # Set up the DCE mock with response containing summary and next steps
        mock_dce = AsyncMock()
        mock_dce.process.return_value = create_agent_response(
            "This is the summary of the process.\n\n## Next Steps\n1. Step one\n2. Step two"
        )
        mock_create_dce.return_value = mock_dce

        # Create a test iteration with critical analysis completed
        session_id = str(uuid.uuid4())
        iteration_id = str(uuid.uuid4())
        iteration = {
            "id": iteration_id,
            "session_id": session_id,
            "number": 1,
            "problem_statement": "Test problem statement",
            "start_time": "2023-01-01T00:00:00",
            "stages": {
                ProcessStage.PROBLEM_UNPACKING.value: {
                    "completed_at": "2023-01-01T00:01:00",
                    "result": "Problem analysis text"
                },
                ProcessStage.EXPERTISE_ASSEMBLY.value: {
                    "completed_at": "2023-01-01T00:02:00",
                    "result": "Expertise assembly result"
                },
                ProcessStage.COLLABORATIVE_IDEATION.value: {
                    "completed_at": "2023-01-01T00:03:00",
                    "result": {"Expert1": "Contribution 1", "Expert2": "Contribution 2"}
                },
                ProcessStage.CRITICAL_ANALYSIS.value: {
                    "completed_at": "2023-01-01T00:04:00",
                    "result": "Critical analysis result"
                }
            },
            "required_experts": ["Expert1", "Expert2"],
            "expertise_contributions": {
                "Expert1": "Contribution 1",
                "Expert2": "Contribution 2"
            },
            "critical_analysis": "Critical analysis result",
            "summary": None,
            "next_steps": None,
            "complete": False
        }
        manager.iterations[iteration_id] = iteration
        manager.session_iterations[session_id] = [iteration_id]

        # Continue to summary and next steps
        iteration = await manager.continue_iteration(session_id, iteration_id)

        # Verify the stage was executed
        assert ProcessStage.SUMMARY_AND_NEXT_STEPS.value in iteration["stages"]
        assert iteration["summary"] is not None
        assert iteration["next_steps"] is not None
        assert "summary" in iteration["summary"].lower()
        assert "step" in iteration["next_steps"].lower()
        assert iteration["complete"] is True

    @pytest.mark.asyncio
    async def test_get_iteration(self, manager):
        """Test getting an iteration."""
        # Create a test iteration
        session_id = str(uuid.uuid4())
        iteration_id = str(uuid.uuid4())
        iteration = {
            "id": iteration_id,
            "session_id": session_id,
            "number": 1,
            "problem_statement": "Test problem statement",
            "start_time": "2023-01-01T00:00:00",
            "stages": {},
            "required_experts": [],
            "expertise_contributions": {},
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }
        manager.iterations[iteration_id] = iteration
        manager.session_iterations[session_id] = [iteration_id]

        # Get the iteration
        result = await manager.get_iteration(session_id, iteration_id)

        # Verify the correct iteration was returned
        assert result == iteration

        # Test not found case
        invalid_id = str(uuid.uuid4())
        not_found = await manager.get_iteration(session_id, invalid_id)
        assert not_found is None

    def test_list_iterations(self, manager):
        """Test listing iterations."""
        # Create test iterations
        session_id = str(uuid.uuid4())
        iteration_ids = [str(uuid.uuid4()) for _ in range(3)]

        for i, iteration_id in enumerate(iteration_ids):
            iteration = {
                "id": iteration_id,
                "session_id": session_id,
                "number": i + 1,
                "problem_statement": f"Test problem {i+1}",
                "start_time": "2023-01-01T00:00:00",
                "stages": {},
                "required_experts": [],
                "expertise_contributions": {},
                "critical_analysis": None,
                "summary": None,
                "next_steps": None,
                "complete": False
            }
            manager.iterations[iteration_id] = iteration

        manager.session_iterations[session_id] = iteration_ids

        # List iterations
        iterations = manager.list_iterations(session_id)

        # Verify all iterations were returned
        assert len(iterations) == 3
        assert {iteration["id"] for iteration in iterations} == set(iteration_ids)