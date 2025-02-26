"""
Test script for validating GitHub repositories and Docker containers with real repositories.

This script tests the integration between GitHub validator and Docker container
with actual repositories of different types.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the parent directory to the Python path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.github.validator import GitHubRepoValidator
from agents.docker.container import DockerContainerAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test repositories
TEST_REPOSITORIES = [
    # Python repositories
    "https://github.com/pallets/flask.git",  # Flask web framework
    "https://github.com/django/django.git",  # Django web framework
    "https://github.com/psf/requests.git",   # Requests HTTP library

    # Node.js repositories
    "https://github.com/expressjs/express.git",  # Express web framework
    "https://github.com/facebook/react.git",     # React UI library
    "https://github.com/nodejs/node.git",        # Node.js itself

    # Java repositories
    "https://github.com/spring-projects/spring-boot.git",  # Spring Boot framework
    "https://github.com/google/guava.git",                # Google's Guava library
]

async def test_repository(repository_url: str, test_mode: bool = False):
    """Test a single repository with GitHub validator and Docker container."""
    logger.info(f"Testing repository: {repository_url}")

    # Initialize components
    validator = GitHubRepoValidator(test_mode=test_mode)
    docker_agent = DockerContainerAgent(test_mode=test_mode)

    # Step 1: Validate repository
    valid_result = validator.validate_repository(repository_url)
    if not valid_result.get("valid"):
        logger.error(f"Repository validation failed: {valid_result.get('error')}")
        return False

    logger.info(f"Repository validation successful: {repository_url}")

    # Step 2: Get repository metadata
    repo_info = validator.get_repository_metadata(repository_url)
    if not repo_info.get("project_type"):
        logger.error(f"Failed to determine project type for {repository_url}")
        return False

    project_type = repo_info.get("project_type")
    logger.info(f"Detected project type: {project_type}")

    # Skip Docker operations if in test mode
    if test_mode:
        logger.info("Skipping Docker operations in test mode")
        return True

    # Step 3: Create Docker container
    container = docker_agent.create_container(repo_info)
    if not container.get("success"):
        logger.error(f"Container creation failed: {container.get('error')}")
        return False

    container_id = container.get("container_id")
    logger.info(f"Created container: {container_id}")

    # Step 4: Setup container for project type
    setup_result = docker_agent.setup_for_project_type(container_id, repo_info)
    if not setup_result.get("success"):
        logger.error(f"Container setup failed: {setup_result.get('error')}")
        # Clean up container
        docker_agent.remove_container(container_id)
        return False

    logger.info(f"Container setup successful for {project_type}")

    # Step 5: Install repository (with a timeout for large repos)
    logger.info(f"Installing repository {repository_url}...")
    install_result = docker_agent.install_repository(container_id, repo_info)
    if not install_result.get("success"):
        logger.error(f"Repository installation failed: {install_result.get('error')}")
        # Clean up container
        docker_agent.remove_container(container_id)
        return False

    logger.info(f"Repository installation successful")

    # Step 6: Install dependencies (with a timeout for large repos)
    logger.info(f"Installing dependencies...")
    dependency_result = docker_agent.install_dependencies(container_id, repo_info)
    if not dependency_result.get("success"):
        logger.error(f"Dependency installation failed: {dependency_result.get('error')}")
        # Clean up container
        docker_agent.remove_container(container_id)
        return False

    logger.info(f"Dependency installation successful")

    # Step 7: Run tests (optional based on repository)
    if "test_command" in repo_info:
        logger.info(f"Running tests...")
        test_result = docker_agent.run_tests(container_id, repo_info)
        logger.info(f"Test execution result: {test_result.get('passed', False)}")
    else:
        logger.info(f"No test command specified, skipping tests")

    # Clean up container
    cleanup_result = docker_agent.remove_container(container_id)
    logger.info(f"Container cleanup: {cleanup_result.get('success', False)}")

    return True

async def test_all_repositories(test_mode: bool = False):
    """Test all repositories in the list."""
    results = {}

    for repo_url in TEST_REPOSITORIES:
        try:
            success = await test_repository(repo_url, test_mode)
            results[repo_url] = "SUCCESS" if success else "FAILED"
        except Exception as e:
            logger.error(f"Error testing {repo_url}: {str(e)}")
            results[repo_url] = f"ERROR: {str(e)}"

    # Print summary
    logger.info("\n\n==== TEST RESULTS SUMMARY ====")
    for repo, result in results.items():
        logger.info(f"{repo}: {result}")

def main():
    """Main entry point for the script."""
    import argparse
    parser = argparse.ArgumentParser(description="Test GitHub repositories with Docker containers")
    parser.add_argument("--test-mode", action="store_true", help="Run in test mode (no actual API or Docker operations)")
    parser.add_argument("--repo", type=str, help="Test a single repository URL")
    args = parser.parse_args()

    # Run with asyncio
    if args.repo:
        asyncio.run(test_repository(args.repo, args.test_mode))
    else:
        asyncio.run(test_all_repositories(args.test_mode))

if __name__ == "__main__":
    main()