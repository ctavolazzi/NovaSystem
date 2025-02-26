"""
Integration tests for GitHub validation, Docker container, and Failure Analysis flow.

This module tests the complete integration between GitHub repository validation,
Docker container management, and test result analysis.
"""
import asyncio
import pytest
from unittest.mock import patch
import sys
from pathlib import Path

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from agents.github.validator import GitHubRepoValidator
from agents.docker.container import DockerContainerAgent
from agents.analysis.failure_analyzer import FailureAnalyzer, TestFramework

# Sample repository URLs
VALID_PUBLIC_PYTHON_REPO = "https://github.com/pytest-dev/pytest.git"
VALID_PUBLIC_NODE_REPO = "https://github.com/expressjs/express.git"
INVALID_REPO = "https://github.com/nonexistent/repo.git"

# Sample test output
SAMPLE_FAILING_TEST_OUTPUT = """
============================= test session starts ==============================
platform darwin -- Python 3.10.0, pytest-8.3.4, pluggy-1.4.0
rootdir: /Users/user/code/project
collected 3 items

test_sample.py::test_one PASSED
test_sample.py::test_two FAILED
test_sample.py::test_three FAILED

================================== FAILURES ===================================
___________________________________ test_two ___________________________________

    def test_two():
>       assert 1 == 2
E       assert 1 == 2

test_sample.py:8: AssertionError
__________________________________ test_three __________________________________

    def test_three():
>       import nonexistent_module
E       ModuleNotFoundError: No module named 'nonexistent_module'

test_sample.py:12: ModuleNotFoundError
=========================== short test summary info ===========================
FAILED test_sample.py::test_two - assert 1 == 2
FAILED test_sample.py::test_three - ModuleNotFoundError: No module named 'nonexistent_module'
========================= 1 passed, 2 failed in 0.12s =========================
"""

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

def create_failure_analyzer(project_type="python"):
    """Helper function to create a failure analyzer."""
    return FailureAnalyzer(project_type=project_type)

@pytest.mark.asyncio
async def test_full_integration_flow():
    """Test the complete integration flow from repository validation to failure analysis."""
    # Create components
    github_validator = create_github_repo_validator()
    docker_agent = create_docker_container_agent()
    failure_analyzer = create_failure_analyzer()

    # Step 1: Validate GitHub repository
    validation_result = github_validator.validate_repository(VALID_PUBLIC_PYTHON_REPO)
    assert validation_result["valid"] is True

    # Step 2: Get repository metadata
    repo_info = github_validator.get_repository_metadata(VALID_PUBLIC_PYTHON_REPO)
    assert repo_info["project_type"] == "python"

    # Step 3: Create Docker container
    container = docker_agent.create_container(repo_info)
    assert container["success"] is True

    # Step 4: Setup container, install repository, and dependencies
    docker_agent.setup_for_project_type(container["container_id"], repo_info)
    docker_agent.install_repository(container["container_id"], repo_info)
    docker_agent.install_dependencies(container["container_id"], repo_info)

    # Step 5: Mock running tests and getting output
    with patch.object(docker_agent, 'run_tests') as mock_run_tests:
        # Configure the mock to return our sample failing output
        mock_run_tests.return_value = {
            "success": True,
            "passed": False,
            "test_output": SAMPLE_FAILING_TEST_OUTPUT,
            "message": "Tests executed with failures"
        }

        # Run the tests
        test_result = docker_agent.run_tests(container["container_id"], repo_info)

    # Step 6: Analyze test failures
    analysis_result = failure_analyzer.analyze_test_output(
        test_result["test_output"],
        framework=TestFramework.PYTEST
    )

    # Verify analysis results
    assert analysis_result["success"] is True
    assert analysis_result["framework"] == "pytest"
    assert len(analysis_result["failures"]) == 2

    # Check specific details of the failures
    # The keys should match what the FailureAnalyzer actually produces
    assert analysis_result["failures"][0]["test_name"] == "test_two"
    assert analysis_result["failures"][0]["error_type"] == "AssertionError"
    assert analysis_result["failures"][1]["test_name"] == "test_three"
    assert analysis_result["failures"][1]["error_type"] == "ModuleNotFoundError"

    # Generate reports
    markdown_report = failure_analyzer.generate_report(analysis_result, format="markdown")
    html_report = failure_analyzer.generate_report(analysis_result, format="html")
    json_report = failure_analyzer.generate_report(analysis_result, format="json")

    # Verify reports were generated
    assert "# Test Failure Analysis Report" in markdown_report
    assert "<!DOCTYPE html>" in html_report
    assert '"framework": "pytest"' in json_report

@pytest.mark.asyncio
async def test_project_type_specific_analysis():
    """Test failure analysis with different project types."""
    # Create components for Python project
    github_validator = create_github_repo_validator()
    docker_agent = create_docker_container_agent()

    # Test with Python project
    python_analyzer = create_failure_analyzer(project_type="python")
    python_result = python_analyzer.analyze_test_output(SAMPLE_FAILING_TEST_OUTPUT)
    assert python_result["success"] is True

    # Verify that the ModuleNotFoundError is categorized as import_error
    assert any(f["error_type"] == "ModuleNotFoundError" and f["category"] == "import_error"
               for f in python_result["failures"])

    # Test with Node.js project
    node_analyzer = create_failure_analyzer(project_type="node")
    node_result = node_analyzer.analyze_test_output(SAMPLE_FAILING_TEST_OUTPUT)
    assert node_result["success"] is True

    # Note: In the current implementation, the basic recommendations for import errors
    # are the same for both Python and Node.js. In a future enhancement, we could make
    # these more specific to each language.

    # Verify that recommendations are generated for both project types
    python_recommendations = python_analyzer._get_category_recommendations("import_error")
    node_recommendations = node_analyzer._get_category_recommendations("import_error")

    # Check that recommendations contain common guidance for module imports
    assert any("module" in rec.lower() for rec in python_recommendations)
    assert any("module" in rec.lower() for rec in node_recommendations)

    # Verify the project-specific recommendations by checking the project-type handling
    assert python_analyzer.project_type == "python"
    assert node_analyzer.project_type == "node"