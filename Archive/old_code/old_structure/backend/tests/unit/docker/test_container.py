"""
Unit tests for Docker container agent.
"""
import pytest
from agents.docker.container import DockerContainerAgent

class TestDockerContainerAgent:
    """Tests for the DockerContainerAgent class."""

    def test_default_initialization(self):
        """Test initializing the Docker container agent with default settings."""
        agent = DockerContainerAgent(test_mode=True)
        assert agent.test_mode is True
        assert len(agent.containers) == 0
        assert agent.client is None

    def test_container_creation(self):
        """Test creating a new Docker container."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/public-repo.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "public-repo"
        }
        container = agent.create_container(repository_info)
        assert container["success"] is True
        assert "container_id" in container
        assert "container_name" in container
        assert "base_image" in container
        assert container["base_image"] == "python:3.10-slim"

        # Check that the container was added to the registry
        assert container["container_id"] in agent.containers

    def test_container_setup_for_python_project(self):
        """Test setting up a container for a Python project."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/python-project.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "python-project"
        }
        container = agent.create_container(repository_info)
        setup_result = agent.setup_for_project_type(container["container_id"], repository_info)
        assert setup_result["success"] is True
        assert setup_result["project_type"] == "python"
        assert "message" in setup_result

    def test_container_setup_for_node_project(self):
        """Test setting up a container for a Node.js project."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/node-project.git",
            "project_type": "node",
            "owner": "valid",
            "repository": "node-project"
        }
        container = agent.create_container(repository_info)
        setup_result = agent.setup_for_project_type(container["container_id"], repository_info)
        assert setup_result["success"] is True
        assert setup_result["project_type"] == "node"
        assert "message" in setup_result

    def test_repository_installation(self):
        """Test installing a repository in a container."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/public-repo.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "public-repo"
        }
        container = agent.create_container(repository_info)
        install_result = agent.install_repository(container["container_id"], repository_info)
        assert install_result["success"] is True
        assert "message" in install_result
        assert agent.containers[container["container_id"]]["repository_installed"] is True

    def test_dependency_installation(self):
        """Test installing dependencies in a container."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/python-project.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "python-project"
        }
        container = agent.create_container(repository_info)
        agent.install_repository(container["container_id"], repository_info)
        install_result = agent.install_dependencies(container["container_id"], repository_info)
        assert install_result["success"] is True
        assert "message" in install_result
        assert agent.containers[container["container_id"]]["dependencies_installed"] is True

    def test_test_execution(self):
        """Test running tests in a container."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/python-project.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "python-project",
            "test_command": "pytest"
        }
        container = agent.create_container(repository_info)
        agent.install_repository(container["container_id"], repository_info)
        agent.install_dependencies(container["container_id"], repository_info)
        test_result = agent.run_tests(container["container_id"], repository_info)
        assert test_result["success"] is True
        assert "passed" in test_result
        assert "test_output" in test_result
        assert "message" in test_result