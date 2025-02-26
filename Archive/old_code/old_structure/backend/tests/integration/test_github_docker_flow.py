"""
Integration tests for GitHub repository validation and Docker container integration.
"""
import asyncio
import pytest
from agents.github.validator import GitHubRepoValidator
from agents.docker.container import DockerContainerAgent

# Sample repository URLs
VALID_PUBLIC_PYTHON_REPO = "https://github.com/pytest-dev/pytest.git"
VALID_PUBLIC_NODE_REPO = "https://github.com/expressjs/express.git"
INVALID_REPO = "https://github.com/nonexistent/repo.git"

def create_github_repo_validator(config=None):
    """Helper function to create a GitHub repository validator."""
    if config is None:
        config = {"test_mode": True}
    return GitHubRepoValidator(test_mode=config.get("test_mode", True))

def create_docker_container_agent(config=None):
    """Helper function to create a Docker container agent."""
    if config is None:
        config = {"test_mode": True}
    return DockerContainerAgent(test_mode=config.get("test_mode", True))

@pytest.mark.asyncio
async def test_basic_github_validation():
    """Test basic GitHub repository validation."""
    validator = create_github_repo_validator()

    # Test valid repository
    valid_result = validator.validate_repository(VALID_PUBLIC_PYTHON_REPO)
    assert valid_result["valid"] is True

    # Test invalid repository
    invalid_result = validator.validate_repository(INVALID_REPO)
    assert invalid_result["valid"] is False

@pytest.mark.asyncio
async def test_repository_metadata_extraction():
    """Test repository metadata extraction."""
    validator = create_github_repo_validator()

    # Get Python repository metadata
    python_repo_info = validator.get_repository_metadata(VALID_PUBLIC_PYTHON_REPO)
    assert python_repo_info["url"] == VALID_PUBLIC_PYTHON_REPO
    assert python_repo_info["project_type"] == "python"

    # Get Node.js repository metadata
    node_repo_info = validator.get_repository_metadata(VALID_PUBLIC_NODE_REPO)
    assert node_repo_info["url"] == VALID_PUBLIC_NODE_REPO
    assert node_repo_info["project_type"] == "node"

@pytest.mark.asyncio
async def test_docker_container_creation():
    """Test Docker container creation."""
    # Create validator and Docker agent in test mode
    validator = create_github_repo_validator(config={"test_mode": True})
    docker_agent = create_docker_container_agent(config={"test_mode": True})

    # Get repository metadata
    repo_info = validator.get_repository_metadata(VALID_PUBLIC_PYTHON_REPO)

    # Create Docker container
    container = docker_agent.create_container(repo_info)
    assert container["success"] is True
    assert "container_id" in container
    assert "container_name" in container
    assert container["base_image"] == "python:3.10-slim"

@pytest.mark.asyncio
async def test_repository_installation():
    """Test repository installation in Docker container."""
    # Create validator and Docker agent in test mode
    validator = create_github_repo_validator(config={"test_mode": True})
    docker_agent = create_docker_container_agent(config={"test_mode": True})

    # Get repository metadata
    repo_info = validator.get_repository_metadata(VALID_PUBLIC_PYTHON_REPO)

    # Create Docker container
    container = docker_agent.create_container(repo_info)

    # Install repository
    result = docker_agent.install_repository(container["container_id"], repo_info)
    assert result["success"] is True
    assert "message" in result

@pytest.mark.asyncio
async def test_full_setup_flow():
    """Test full setup flow from validation to test execution."""
    # Create validator and Docker agent in test mode
    validator = create_github_repo_validator(config={"test_mode": True})
    docker_agent = create_docker_container_agent(config={"test_mode": True})

    # Get repository metadata
    repo_info = validator.get_repository_metadata(VALID_PUBLIC_PYTHON_REPO)

    # Create Docker container
    container = docker_agent.create_container(repo_info)

    # Setup container
    setup_result = docker_agent.setup_for_project_type(container["container_id"], repo_info)
    assert setup_result["success"] is True

    # Install repository
    install_result = docker_agent.install_repository(container["container_id"], repo_info)
    assert install_result["success"] is True

    # Install dependencies
    dependency_result = docker_agent.install_dependencies(container["container_id"], repo_info)
    assert dependency_result["success"] is True

    # Run tests
    test_result = docker_agent.run_tests(container["container_id"], repo_info)
    assert test_result["success"] is True
    assert test_result["passed"] is True

@pytest.mark.asyncio
async def test_failing_project():
    """Test a failing project."""
    # Create validator and Docker agent in test mode
    validator = create_github_repo_validator(config={"test_mode": True})
    docker_agent = create_docker_container_agent(config={"test_mode": True})

    # Use a repository name that will trigger a test failure
    repo_url = "https://github.com/test/failing-project.git"

    # Get repository metadata
    repo_info = validator.get_repository_metadata(repo_url)

    # Create Docker container
    container = docker_agent.create_container(repo_info)

    # Setup container
    docker_agent.setup_for_project_type(container["container_id"], repo_info)

    # Install repository
    docker_agent.install_repository(container["container_id"], repo_info)

    # Install dependencies
    docker_agent.install_dependencies(container["container_id"], repo_info)

    # Run tests (should indicate failure)
    test_result = docker_agent.run_tests(container["container_id"], repo_info)
    assert test_result["success"] is True  # The command executed successfully
    assert test_result["passed"] is False  # But the tests themselves failed