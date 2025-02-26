#!/usr/bin/env python
"""
Semi-Autonomous GitHub Docker Integration for NovaSystem

This script provides a high-level interface for the GitHub Docker integration,
automating the process of validating, setting up, testing, and analyzing
GitHub repositories in Docker containers with minimal user intervention.

Usage:
    python auto_github_docker.py <repo_url> [options]

Example:
    python auto_github_docker.py https://github.com/username/repository.git --analyze --cleanup
    python auto_github_docker.py https://github.com/username/repository.git --test-mode --simulate-failing-tests --analyze
"""

import os
import sys
import argparse
import logging
import json
import time
import tempfile
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("novasystem-auto")

# Add the parent directory to path to allow imports
script_path = Path(__file__).absolute()
sys.path.insert(0, str(script_path.parent))  # Add NovaSystem to the path

# Try to import from installed package first, then fallback to local import
try:
    from novasystem.backend.cli.github_docker_cli import (
        validate_repository, setup_repository, run_tests,
        analyze_results, clean_container
    )
    logger.info("Using NovaSystem from PyPI")
    USING_PYPI = True
except ImportError:
    logger.info("NovaSystem PyPI package not found, using local import")

    # Direct import from local paths
    sys.path.insert(0, str(script_path.parent))  # Ensure parent directory is in path

    # Import the functions directly
    from backend.cli.github_docker_cli import (
        validate_repository, setup_repository, run_tests,
        analyze_results, clean_container
    )
    USING_PYPI = False
    logger.info("Using local NovaSystem import")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Semi-autonomous GitHub Docker integration for NovaSystem"
    )

    parser.add_argument(
        "repository_url",
        help="URL of the GitHub repository to process"
    )

    parser.add_argument(
        "--token",
        help="GitHub token for private repositories"
    )

    parser.add_argument(
        "--env",
        action="append",
        help="Environment variables (format: KEY=VALUE)"
    )

    parser.add_argument(
        "--test-command",
        help="Custom test command to run (default: auto-detected based on project type)"
    )

    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze test results"
    )

    parser.add_argument(
        "--report-format",
        choices=["json", "html", "markdown"],
        default="html",
        help="Format for the analysis report (default: html)"
    )

    parser.add_argument(
        "--output-dir",
        help="Directory to save reports (default: current directory)"
    )

    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Remove the Docker container after testing"
    )

    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode (no actual API or Docker operations)"
    )

    parser.add_argument(
        "--simulate-failing-tests",
        action="store_true",
        help="Simulate failing tests in test mode"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    return parser.parse_args()

def create_args_namespace(args_dict):
    """Create an argparse.Namespace object from a dictionary."""
    namespace = argparse.Namespace()
    for key, value in args_dict.items():
        setattr(namespace, key, value)
    return namespace

def generate_output_filename(repo_url, format):
    """Generate a filename for the output report based on the repository name and timestamp."""
    # Extract repository name from URL
    repo_name = repo_url.split('/')[-1]
    if repo_name.endswith('.git'):
        repo_name = repo_name[:-4]

    timestamp = time.strftime("%Y%m%d-%H%M%S")
    return f"{repo_name}-report-{timestamp}.{format}"

def run_autonomous_flow(args):
    """Run the semi-autonomous GitHub Docker integration flow."""
    output_dir = args.output_dir or os.getcwd()
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Create agent instances that we'll reuse across operations in test mode
    if args.test_mode:
        # Import here to avoid circular imports
        from backend.agents.docker.container import DockerContainerAgent
        from backend.agents.github.validator import GitHubRepoValidator

        # Create instances that we'll reuse
        docker_agent = DockerContainerAgent(test_mode=True)
        github_validator = GitHubRepoValidator(test_mode=True)

        # If simulating failing tests, we need to remember this for later
        if args.simulate_failing_tests:
            logger.info("Simulating failing tests")
    else:
        docker_agent = None
        github_validator = None

    # Step 1: Validate repository
    logger.info(f"Validating repository: {args.repository_url}")
    validation_args = create_args_namespace({
        "repository_url": args.repository_url,
        "token": args.token,
        "test_mode": args.test_mode,
        "github_validator": github_validator
    })
    validation_result = validate_repository(validation_args)
    if validation_result != 0:
        logger.error("Repository validation failed")
        return validation_result

    # Step 2: Setup repository in Docker container
    logger.info(f"Setting up repository in Docker container: {args.repository_url}")
    setup_args = create_args_namespace({
        "repository_url": args.repository_url,
        "token": args.token,
        "env": args.env,
        "test_mode": args.test_mode,
        "github_validator": github_validator,
        "docker_agent": docker_agent
    })

    # Use temporary file to capture stdout during setup
    import io
    original_stdout = sys.stdout
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        setup_result = setup_repository(setup_args)
        sys.stdout = original_stdout

        if setup_result != 0:
            logger.error("Repository setup failed")
            return setup_result

        # Extract container ID from captured output
        setup_output = captured_output.getvalue()
        container_id = None
        import json
        import re

        # Try to parse JSON output to get container_id
        try:
            match = re.search(r'{\s*"success":\s*true.*?"container_id":\s*"([^"]+)"', setup_output, re.DOTALL)
            if match:
                container_id = match.group(1)
        except Exception as e:
            logger.debug(f"Error extracting container ID from JSON: {e}")

        if not container_id and docker_agent:
            # If we have a docker agent, get the last created container
            if docker_agent.containers:
                container_id = list(docker_agent.containers.keys())[-1]
                logger.info(f"Using last created container ID: {container_id}")

        if not container_id:
            logger.error("Failed to get container ID from setup output")
            return 1

        logger.info(f"Container created with ID: {container_id}")

        # Step 3: Run tests in Docker container
        logger.info(f"Running tests in container: {container_id}")

        # Generate output filename
        output_filename = None
        if args.analyze:
            repo_name = args.repository_url.split('/')[-1]
            if repo_name.endswith('.git'):
                repo_name = repo_name[:-4]
            output_filename = generate_output_filename(repo_name, args.report_format)
            logger.info(f"Test analysis will be saved to: {os.path.join(output_dir, output_filename)}")

        test_args = create_args_namespace({
            "container_id": container_id,
            "test_command": args.test_command,
            "analyze": args.analyze,
            "report_format": args.report_format,
            "output_file": os.path.join(output_dir, output_filename) if output_filename else None,
            "test_mode": args.test_mode,
            "docker_agent": docker_agent,
            "simulate_failing": args.simulate_failing_tests
        })
        test_result = run_tests(test_args)

        # Step 4: Cleanup (if requested)
        if args.cleanup:
            logger.info(f"Cleaning up container: {container_id}")
            cleanup_args = create_args_namespace({
                "container_id": container_id,
                "test_mode": args.test_mode,
                "docker_agent": docker_agent
            })
            cleanup_result = clean_container(cleanup_args)
            if cleanup_result == 0:
                logger.info("Container successfully removed")
            else:
                logger.warning("Container cleanup failed")

        logger.info("GitHub Docker integration flow completed successfully")
        return 0
    finally:
        # Ensure we reset stdout even if an exception occurs
        sys.stdout = original_stdout

def main():
    """Main entry point for the script."""
    args = parse_args()

    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        logger.info("Starting semi-autonomous GitHub Docker integration flow")
        result = run_autonomous_flow(args)

        if result == 0:
            logger.info("GitHub Docker integration flow completed successfully")
        else:
            logger.error(f"GitHub Docker integration flow failed with exit code {result}")

        return result

    except Exception as e:
        logger.exception(f"Unhandled error in GitHub Docker integration flow: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())