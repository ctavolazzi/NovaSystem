"""
Unit tests for Docker container environment variables.
"""
import pytest
from agents.docker.container import DockerContainerAgent

class TestDockerContainerEnvironment:
    """Tests for environment variables in Docker containers."""

    def test_create_with_environment(self):
        """Test creating a container with environment variables."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/public-repo.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "public-repo"
        }
        custom_env = {
            "TEST_VAR1": "test_value1",
            "TEST_VAR2": "test_value2",
            "DEBUG": "true"
        }
        container = agent.create_container(repository_info, environment=custom_env)

        # Check default environment variables
        assert container["success"] is True
        assert "environment" in container
        assert container["environment"]["PROJECT_TYPE"] == "python"
        assert container["environment"]["REPOSITORY_URL"] == repository_info["url"]
        assert container["environment"]["REPOSITORY_OWNER"] == repository_info["owner"]
        assert container["environment"]["REPOSITORY_NAME"] == repository_info["repository"]

        # Check custom environment variables
        assert container["environment"]["TEST_VAR1"] == "test_value1"
        assert container["environment"]["TEST_VAR2"] == "test_value2"
        assert container["environment"]["DEBUG"] == "true"

    def test_update_environment(self):
        """Test updating environment variables in a container."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/public-repo.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "public-repo"
        }
        container = agent.create_container(repository_info)

        # Update environment variables
        update_env = {
            "DEBUG": "true",
            "LOG_LEVEL": "INFO",
            "APP_PORT": "8080"
        }
        result = agent.update_environment(container["container_id"], update_env)

        # Check that the update was successful
        assert result["success"] is True
        assert "environment" in result
        assert result["environment"]["DEBUG"] == "true"
        assert result["environment"]["LOG_LEVEL"] == "INFO"
        assert result["environment"]["APP_PORT"] == "8080"

        # Get all environment variables
        get_result = agent.get_environment(container["container_id"])

        # Check that the environment variables were updated
        assert get_result["success"] is True
        assert "environment" in get_result
        assert get_result["environment"]["DEBUG"] == "true"
        assert get_result["environment"]["LOG_LEVEL"] == "INFO"
        assert get_result["environment"]["APP_PORT"] == "8080"

        # Original environment variables should still be there
        assert get_result["environment"]["PROJECT_TYPE"] == "python"
        assert get_result["environment"]["REPOSITORY_URL"] == repository_info["url"]

    def test_get_specific_environment_variables(self):
        """Test getting specific environment variables from a container."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/public-repo.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "public-repo"
        }
        custom_env = {
            "TEST_VAR1": "test_value1",
            "TEST_VAR2": "test_value2",
            "DEBUG": "true"
        }
        container = agent.create_container(repository_info, environment=custom_env)

        # Get specific environment variables
        specific_vars = ["DEBUG", "TEST_VAR1"]
        result = agent.get_environment(container["container_id"], variables=specific_vars)

        # Check that only the requested variables are returned
        assert result["success"] is True
        assert "environment" in result
        assert len(result["environment"]) == 2
        assert "DEBUG" in result["environment"]
        assert "TEST_VAR1" in result["environment"]
        assert "TEST_VAR2" not in result["environment"]
        assert "PROJECT_TYPE" not in result["environment"]

    def test_environment_with_special_characters(self):
        """Test environment variables with special characters."""
        agent = DockerContainerAgent(test_mode=True)
        repository_info = {
            "url": "https://github.com/valid/public-repo.git",
            "project_type": "python",
            "owner": "valid",
            "repository": "public-repo"
        }

        # Environment with special characters
        special_env = {
            "PATH_WITH_SPACES": "/path with spaces/bin",
            "QUOTED_VALUE": "\"quoted string\"",
            "WITH_SINGLE_QUOTES": "it's a test",
            "WITH_NEWLINE": "line1\nline2",
            "WITH_EQUALS": "key=value"
        }

        container = agent.create_container(repository_info, environment=special_env)

        # Get environment variables
        result = agent.get_environment(container["container_id"])

        # Check that special characters are handled correctly
        assert result["success"] is True
        assert "environment" in result
        assert result["environment"]["PATH_WITH_SPACES"] == "/path with spaces/bin"
        assert result["environment"]["QUOTED_VALUE"] == "\"quoted string\""
        assert result["environment"]["WITH_SINGLE_QUOTES"] == "it's a test"
        assert result["environment"]["WITH_NEWLINE"] == "line1\nline2"
        assert result["environment"]["WITH_EQUALS"] == "key=value"

    def test_nonexistent_container(self):
        """Test operations on a nonexistent container."""
        agent = DockerContainerAgent(test_mode=True)

        # Try to update environment in a nonexistent container
        result = agent.update_environment("nonexistent-id", {"TEST": "value"})
        assert result["success"] is False
        assert "error" in result

        # Try to get environment from a nonexistent container
        result = agent.get_environment("nonexistent-id")
        assert result["success"] is False
        assert "error" in result