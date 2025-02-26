"""
NovaProcess manager.

This module provides functionality for orchestrating the Nova Process,
a multi-agent problem-solving workflow.
"""
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional

from agents.factory import create_agent, create_dce_agent, create_cae_agent, create_domain_expert_agent

logger = logging.getLogger(__name__)


class ProcessStage(Enum):
    """Stages of the Nova Process."""
    PROBLEM_UNPACKING = "problem_unpacking"
    EXPERTISE_ASSEMBLY = "expertise_assembly"
    COLLABORATIVE_IDEATION = "collaborative_ideation"
    CRITICAL_ANALYSIS = "critical_analysis"
    SUMMARY_AND_NEXT_STEPS = "summary_and_next_steps"


class NovaProcessManager:
    """
    Manager for the Nova Process.

    This class manages the execution of the Nova Process workflow,
    coordinating the activities of different agents.
    """

    def __init__(self):
        """Initialize the Nova Process manager."""
        self.sessions = {}  # Maps session_id to session data
        self.iterations = {}  # Maps iteration_id to iteration data
        self.session_iterations = {}  # Maps session_id to list of iteration_ids

    async def start_iteration(self, session_id: str, problem_statement: str) -> Dict[str, Any]:
        """
        Start a new iteration of the Nova Process.

        Args:
            session_id: The ID of the session.
            problem_statement: The problem statement to address.

        Returns:
            Dictionary containing iteration data.
        """
        iteration_id = str(uuid.uuid4())

        # Get the current iterations for this session, or create a new list
        session_iterations = self.session_iterations.get(session_id, [])

        # Create iteration data
        iteration = {
            "id": iteration_id,
            "session_id": session_id,
            "number": len(session_iterations) + 1,
            "problem_statement": problem_statement,
            "start_time": datetime.utcnow().isoformat(),
            "stages": {},
            "required_experts": [],
            "expertise_contributions": {},
            "critical_analysis": None,
            "summary": None,
            "next_steps": None,
            "complete": False
        }

        # Store in our data structures
        self.iterations[iteration_id] = iteration
        session_iterations.append(iteration_id)
        self.session_iterations[session_id] = session_iterations

        # Begin with problem unpacking
        await self._execute_stage(iteration_id, ProcessStage.PROBLEM_UNPACKING)

        return iteration

    async def continue_iteration(self, session_id: str, iteration_id: str) -> Dict[str, Any]:
        """
        Continue an in-progress iteration to the next stage.

        Args:
            session_id: The ID of the session.
            iteration_id: The ID of the iteration to continue.

        Returns:
            Dictionary containing updated iteration data.

        Raises:
            ValueError: If iteration is not found or doesn't belong to session.
        """
        # Validate iteration exists and belongs to this session
        if iteration_id not in self.iterations:
            raise ValueError(f"Iteration with ID {iteration_id} not found")

        iteration = self.iterations[iteration_id]
        if iteration["session_id"] != session_id:
            raise ValueError(f"Iteration {iteration_id} does not belong to session {session_id}")

        # Determine the next stage
        completed_stages = list(iteration["stages"].keys())

        if ProcessStage.PROBLEM_UNPACKING.value in completed_stages:
            if ProcessStage.EXPERTISE_ASSEMBLY.value not in completed_stages:
                await self._execute_stage(iteration_id, ProcessStage.EXPERTISE_ASSEMBLY)

        if ProcessStage.EXPERTISE_ASSEMBLY.value in completed_stages:
            if ProcessStage.COLLABORATIVE_IDEATION.value not in completed_stages:
                await self._execute_stage(iteration_id, ProcessStage.COLLABORATIVE_IDEATION)

        if ProcessStage.COLLABORATIVE_IDEATION.value in completed_stages:
            if ProcessStage.CRITICAL_ANALYSIS.value not in completed_stages:
                await self._execute_stage(iteration_id, ProcessStage.CRITICAL_ANALYSIS)

        if ProcessStage.CRITICAL_ANALYSIS.value in completed_stages:
            if ProcessStage.SUMMARY_AND_NEXT_STEPS.value not in completed_stages:
                await self._execute_stage(iteration_id, ProcessStage.SUMMARY_AND_NEXT_STEPS)
                iteration["complete"] = True

        return iteration

    async def get_iteration(self, session_id: str, iteration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an iteration by ID.

        Args:
            session_id: The ID of the session.
            iteration_id: The ID of the iteration to get.

        Returns:
            Dictionary containing iteration data, or None if not found.
        """
        if iteration_id not in self.iterations:
            return None

        iteration = self.iterations[iteration_id]
        if iteration["session_id"] != session_id:
            return None

        return iteration

    def list_iterations(self, session_id: str) -> List[Dict[str, Any]]:
        """
        List all iterations for a session.

        Args:
            session_id: The ID of the session.

        Returns:
            List of iteration data dictionaries.
        """
        iteration_ids = self.session_iterations.get(session_id, [])
        return [self.iterations[iteration_id] for iteration_id in iteration_ids
                if iteration_id in self.iterations]

    async def _execute_stage(self, iteration_id: str, stage: ProcessStage) -> None:
        """
        Execute a specific stage of the Nova Process.

        Args:
            iteration_id: The ID of the iteration.
            stage: The stage to execute.

        Raises:
            ValueError: If iteration is not found.
        """
        iteration = self.iterations.get(iteration_id)
        if not iteration:
            raise ValueError(f"Iteration with ID {iteration_id} not found")

        logger.info(f"Executing {stage.value} for iteration {iteration_id}")

        if stage == ProcessStage.PROBLEM_UNPACKING:
            # Use the DCE to break down the problem
            dce = create_dce_agent()

            response = await dce.process({
                "message": f"Analyze and break down the following problem into its key components and dimensions:\n\n{iteration['problem_statement']}"
            })

            iteration["stages"][stage.value] = {
                "completed_at": datetime.utcnow().isoformat(),
                "result": response.get("response", "")
            }

        elif stage == ProcessStage.EXPERTISE_ASSEMBLY:
            # Determine which expertise domains are needed
            problem_analysis = iteration["stages"][ProcessStage.PROBLEM_UNPACKING.value]["result"]

            # Use the DCE to identify required expertise
            dce = create_dce_agent()
            expertise_response = await dce.process({
                "message": f"Based on this problem analysis, identify the specific domains of expertise needed to address this problem effectively:\n\n{problem_analysis}",
                "context": {
                    "problem_statement": iteration["problem_statement"]
                }
            })

            # Extract and clean up the list of required experts
            # This is a simplified approach - in a real implementation, you might use
            # structured outputs from the LLM or a more sophisticated parsing approach
            expertise_list = expertise_response.get("response", "").split('\n')
            required_experts = [
                exp.strip().strip('-').strip().strip(':').strip()
                for exp in expertise_list
                if exp.strip() and not exp.strip().startswith('#')
            ]

            # Filter out non-domain items and duplicates
            required_experts = [
                exp for exp in required_experts
                if len(exp) > 2 and not exp.lower().startswith(("domain", "expert", "expertise", "specialist", "following", "we need", "required"))
            ]
            required_experts = list(set(required_experts))

            iteration["required_experts"] = required_experts
            iteration["stages"][stage.value] = {
                "completed_at": datetime.utcnow().isoformat(),
                "result": expertise_response.get("response", "")
            }

        elif stage == ProcessStage.COLLABORATIVE_IDEATION:
            # Collect input from all relevant experts
            problem_statement = iteration["problem_statement"]
            problem_analysis = iteration["stages"][ProcessStage.PROBLEM_UNPACKING.value]["result"]

            expertise_contributions = {}

            # First get input from DCE
            dce = create_dce_agent()
            dce_response = await dce.process({
                "message": f"Provide initial guidance on approaching this problem:",
                "context": {
                    "problem_statement": problem_statement,
                    "problem_analysis": problem_analysis
                }
            })
            expertise_contributions["Discussion Continuity Expert"] = dce_response.get("response", "")

            # Get input from each domain expert
            for domain in iteration["required_experts"]:
                expert = create_domain_expert_agent(domain=domain)
                expert_response = await expert.process({
                    "message": f"Provide your specialized input on this problem from your perspective as a {domain} expert:",
                    "context": {
                        "problem_statement": problem_statement,
                        "problem_analysis": problem_analysis
                    }
                })
                expertise_contributions[domain] = expert_response.get("response", "")

            iteration["expertise_contributions"] = expertise_contributions
            iteration["stages"][stage.value] = {
                "completed_at": datetime.utcnow().isoformat(),
                "result": expertise_contributions
            }

        elif stage == ProcessStage.CRITICAL_ANALYSIS:
            # Use CAE to critically analyze the contributions
            cae = create_cae_agent()

            # Format the expert contributions for analysis
            contributions_text = "\n\n".join([
                f"**{expert}**:\n{contribution}"
                for expert, contribution in iteration["expertise_contributions"].items()
            ])

            analysis_response = await cae.process({
                "message": f"Critically analyze the expert contributions on this problem:",
                "context": {
                    "problem_statement": iteration["problem_statement"]
                },
                "proposed_solution": contributions_text
            })

            analysis = analysis_response.get("response", "")
            iteration["critical_analysis"] = analysis
            iteration["stages"][stage.value] = {
                "completed_at": datetime.utcnow().isoformat(),
                "result": analysis
            }

        elif stage == ProcessStage.SUMMARY_AND_NEXT_STEPS:
            # Use DCE to summarize progress and recommend next steps
            dce = create_dce_agent()

            # Prepare the context from previous stages
            problem_analysis = iteration["stages"][ProcessStage.PROBLEM_UNPACKING.value]["result"]
            contributions_text = "\n\n".join([
                f"**{expert}**:\n{contribution}"
                for expert, contribution in iteration["expertise_contributions"].items()
            ])
            critical_analysis = iteration["critical_analysis"]

            summary_response = await dce.process({
                "message": f"Summarize the progress made on this problem and recommend specific next steps:",
                "context": {
                    "problem_statement": iteration["problem_statement"],
                    "problem_analysis": problem_analysis,
                    "expert_contributions": contributions_text,
                    "critical_analysis": critical_analysis
                }
            })

            # Parse out summary and next steps
            # This is simplified - a real implementation might use more sophisticated parsing
            summary_text = summary_response.get("response", "")
            parts = summary_text.split("## Next Steps")

            if len(parts) > 1:
                summary = parts[0].strip()
                next_steps = parts[1].strip()
            else:
                # Try alternative formats
                parts = summary_text.split("Next Steps:")
                if len(parts) > 1:
                    summary = parts[0].strip()
                    next_steps = parts[1].strip()
                else:
                    summary = summary_text
                    next_steps = "Not explicitly defined."

            iteration["summary"] = summary
            iteration["next_steps"] = next_steps
            iteration["stages"][stage.value] = {
                "completed_at": datetime.utcnow().isoformat(),
                "result": summary_response.get("response", "")
            }

        logger.info(f"Completed {stage.value} for iteration {iteration_id}")