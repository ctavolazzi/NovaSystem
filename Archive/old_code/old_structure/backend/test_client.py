#!/usr/bin/env python
"""
NovaSystem API Test Client

This script tests the basic functionality of the NovaSystem API,
including session management and the Nova Process execution.
"""
import os
import sys
import json
import time
import logging
import requests
from typing import Dict, Any, Optional, List
from visualization import NovaVisualizer, save_iteration_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nova-test-client")

# API Configuration
API_BASE_URL = "http://localhost:8000"

class NovaTestClient:
    """Test client for the NovaSystem API."""

    def __init__(self, base_url: str = API_BASE_URL, output_dir: str = "debug_output"):
        """Initialize the test client."""
        self.base_url = base_url
        self.session_id = None
        self.output_dir = output_dir

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Initialize the visualizer
        self.visualizer = NovaVisualizer(output_dir=output_dir)

    def health_check(self) -> Dict[str, Any]:
        """Test the health check endpoint."""
        url = f"{self.base_url}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def create_session(self, name: str = "Test Session") -> str:
        """Create a new session."""
        url = f"{self.base_url}/agents/sessions"
        payload = {"name": name}

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        self.session_id = data["id"]
        logger.info(f"Created session: {self.session_id}")
        return self.session_id

    def start_nova_iteration(self, problem_statement: str) -> Dict[str, Any]:
        """Start a new Nova process iteration."""
        if not self.session_id:
            raise ValueError("No active session")

        url = f"{self.base_url}/nova/sessions/{self.session_id}/iterations"
        payload = {"problem_statement": problem_statement}

        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()
        logger.info(f"Started iteration: {data['id']}")

        # Save initial iteration data
        save_iteration_json(data, self.output_dir)

        return data

    def continue_iteration(self, iteration_id: str) -> Dict[str, Any]:
        """Continue an existing iteration to the next stage."""
        if not self.session_id:
            raise ValueError("No active session")

        url = f"{self.base_url}/nova/sessions/{self.session_id}/iterations/{iteration_id}/continue"

        response = requests.post(url)
        response.raise_for_status()

        data = response.json()
        stages = list(data['stages'].keys())
        current_stage = stages[-1] if stages else "unknown"
        logger.info(f"Continued iteration to stage: {current_stage}")

        # Save iteration data after each stage
        save_iteration_json(data, self.output_dir)

        return data

    def process_complete_iteration(self, problem_statement: str, visualize: bool = True) -> Dict[str, Any]:
        """
        Process a complete Nova iteration through all stages.

        Args:
            problem_statement: The problem to solve.
            visualize: Whether to generate visualizations.

        Returns:
            Complete iteration data.
        """
        # Start the iteration
        iteration = self.start_nova_iteration(problem_statement)
        iteration_id = iteration["id"]

        # Continue until complete
        while not iteration.get("complete", False):
            logger.info("Continuing to next stage...")
            time.sleep(1)  # Small delay to avoid hammering the API
            iteration = self.continue_iteration(iteration_id)

            # Print progress
            stages = list(iteration["stages"].keys())
            current_stage = stages[-1] if stages else "unknown"
            logger.info(f"Current stage: {current_stage}")

            # Print details of the current stage
            if stages:
                result = iteration["stages"][current_stage].get("result", "")
                if isinstance(result, str) and len(result) > 100:
                    result = result[:100] + "..."
                logger.info(f"Stage result: {result}")

        logger.info("Iteration complete!")

        # Generate visualizations if requested
        if visualize:
            try:
                # Generate process flow visualization
                self.visualizer.generate_process_graph(iteration)

                # Generate agent interaction visualization
                self.visualizer.generate_agent_interaction_graph(iteration)
            except Exception as e:
                logger.error(f"Error generating visualizations: {str(e)}")

        return iteration

    def get_iteration(self, iteration_id: str) -> Dict[str, Any]:
        """Get an iteration by ID."""
        if not self.session_id:
            raise ValueError("No active session")

        url = f"{self.base_url}/nova/sessions/{self.session_id}/iterations/{iteration_id}"

        response = requests.get(url)
        response.raise_for_status()

        return response.json()

    def list_iterations(self) -> List[Dict[str, Any]]:
        """List all iterations for the current session."""
        if not self.session_id:
            raise ValueError("No active session")

        url = f"{self.base_url}/nova/sessions/{self.session_id}/iterations"

        response = requests.get(url)
        response.raise_for_status()

        return response.json()


def main():
    """Run the test client."""
    client = NovaTestClient()

    try:
        # Test health check
        logger.info("Testing health check...")
        health = client.health_check()
        logger.info(f"Health check successful: {health}")

        # Create session
        logger.info("Creating session...")
        client.create_session("Debug Test Session")

        # Process a complete iteration
        logger.info("Starting Nova Process iteration...")
        problem = "How can we improve customer retention for a SaaS product?"

        iteration = client.process_complete_iteration(problem)

        # Print summary
        logger.info("=== ITERATION SUMMARY ===")
        logger.info(f"Problem: {iteration['problem_statement']}")
        logger.info(f"Experts consulted: {', '.join(iteration['required_experts'])}")
        logger.info(f"Summary: {iteration['summary'][:200]}..." if iteration.get('summary') else "No summary available")
        logger.info(f"Next steps: {iteration['next_steps'][:200]}..." if iteration.get('next_steps') else "No next steps available")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return 1

    logger.info("All tests completed successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())