"""
Unit tests for the Failure Analyzer module.
"""

import pytest
import json
from datetime import datetime
from typing import Dict, Any

from NovaSystem.backend.agents.analysis.failure_analyzer import (
    FailureAnalyzer,
    FailureCategory,
    FailureSeverity,
    TestFramework
)


class TestFailureAnalyzer:
    """Test suite for the FailureAnalyzer class."""

    def test_initialization(self):
        """Test that FailureAnalyzer initializes with default project type."""
        analyzer = FailureAnalyzer()
        assert analyzer.project_type == "unknown"

        analyzer = FailureAnalyzer(project_type="python")
        assert analyzer.project_type == "python"
        assert isinstance(analyzer.patterns, dict)
        assert isinstance(analyzer.recommendations, dict)

    def test_detect_framework(self):
        """Test the framework detection from test output."""
        analyzer = FailureAnalyzer()

        # Test pytest detection
        pytest_output = "===== test session starts ===== collected 5 items ... 5 passed in 0.15s ====="
        assert analyzer._detect_framework(pytest_output) == TestFramework.PYTEST

        # Test Jest detection
        jest_output = "PASS src/components/test.spec.js\n Test Suites: 1 passed, 1 total"
        assert analyzer._detect_framework(jest_output) == TestFramework.JEST

        # Test unknown framework
        unknown_output = "Some random test output that doesn't match any pattern"
        assert analyzer._detect_framework(unknown_output) == TestFramework.UNKNOWN

    def test_parse_pytest_results(self):
        """Test parsing of pytest test results."""
        analyzer = FailureAnalyzer(project_type="python")
        pytest_output = """
===== test session starts =====
platform darwin -- Python 3.10.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/user/project
collected 3 items

test_file.py::test_func1 PASSED
test_file.py::test_func2 FAILED
test_file.py::test_func3 PASSED

==================================== FAILURES ====================================
_________________________________ test_func2 __________________________________

    def test_func2():
>       assert 1 == 2
E       assert 1 == 2

test_file.py:15: AssertionError
========================== short test summary info ===========================
FAILED test_file.py::test_func2 - assert 1 == 2
================= 1 failed, 2 passed, 0 warning in 0.12s ==================
"""
        result = analyzer._parse_pytest_results(pytest_output)

        # Check summary information
        assert "summary" in result
        assert "failures" in result
        assert len(result["failures"]) == 1

        # Check failure details
        failure = result["failures"][0]
        assert failure["test_name"] == "test_func2"
        assert failure["file_path"] == "test_file.py"
        assert failure["line_number"] == 15
        assert failure["error_type"] == "AssertionError"
        assert "assert 1 == 2" in failure["error_message"]

    def test_analyze_test_output_empty(self):
        """Test analyzing empty test output."""
        analyzer = FailureAnalyzer()
        result = analyzer.analyze_test_output("")

        assert result["success"] is False
        assert "No test output provided" in result["error"]
        assert len(result["failures"]) == 0

    def test_analyze_test_output_pytest(self):
        """Test analyzing pytest test output."""
        analyzer = FailureAnalyzer(project_type="python")
        pytest_output = """
===== test session starts =====
platform darwin -- Python 3.10.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/user/project
collected 3 items

test_file.py::test_func1 PASSED
test_file.py::test_func2 FAILED
test_file.py::test_func3 PASSED

==================================== FAILURES ====================================
_________________________________ test_func2 __________________________________

    def test_func2():
>       assert 1 == 2
E       assert 1 == 2

test_file.py:15: AssertionError
========================== short test summary info ===========================
FAILED test_file.py::test_func2 - assert 1 == 2
================= 1 failed, 2 passed, 0 warning in 0.12s ==================
"""
        result = analyzer.analyze_test_output(pytest_output)

        assert result["success"] is True
        assert result["framework"] == TestFramework.PYTEST.value
        assert "summary" in result
        assert len(result["failures"]) == 1
        assert len(result["recommendations"]) == 1

        # Check failure categorization
        failure = result["failures"][0]
        assert failure["category"] == FailureCategory.ASSERTION_ERROR.value
        assert failure["severity"] == FailureSeverity.MEDIUM.value
        assert failure["confidence"] > 0

    def test_categorize_failures(self):
        """Test the failure categorization logic."""
        analyzer = FailureAnalyzer(project_type="python")

        failures = [
            {
                "test_name": "test_syntax",
                "error_type": "SyntaxError",
                "error_message": "invalid syntax",
                "file_path": "file.py",
                "line_number": 10
            },
            {
                "test_name": "test_import",
                "error_type": "ImportError",
                "error_message": "No module named 'nonexistent'",
                "file_path": "file.py",
                "line_number": 20
            },
            {
                "test_name": "test_assertion",
                "error_type": "AssertionError",
                "error_message": "assert 1 == 2",
                "file_path": "file.py",
                "line_number": 30
            }
        ]

        categorized = analyzer._categorize_failures(failures)

        assert len(categorized) == 3
        assert categorized[0]["category"] == FailureCategory.SYNTAX_ERROR.value
        assert categorized[1]["category"] == FailureCategory.IMPORT_ERROR.value
        assert categorized[2]["category"] == FailureCategory.ASSERTION_ERROR.value

    def test_generate_recommendations(self):
        """Test recommendation generation for failures."""
        analyzer = FailureAnalyzer(project_type="python")

        failures = [
            {
                "test_name": "test_import",
                "error_type": "ImportError",
                "error_message": "No module named 'requests'",
                "category": FailureCategory.IMPORT_ERROR.value,
                "severity": FailureSeverity.HIGH.value,
                "confidence": 0.9,
                "file_path": "file.py",
                "line_number": 10
            }
        ]

        recommendations = analyzer._generate_recommendations(failures)

        assert len(recommendations) == 1
        recommendation = recommendations[0]
        assert recommendation["test_name"] == "test_import"
        assert recommendation["category"] == FailureCategory.IMPORT_ERROR.value
        assert len(recommendation["general_recommendations"]) > 0

        # Python import errors should have specific recommendations
        specific_recs = recommendation["specific_recommendations"]
        assert len(specific_recs) > 0
        assert any("pip install" in rec for rec in specific_recs)

    def test_generate_report_formats(self):
        """Test report generation in different formats."""
        analyzer = FailureAnalyzer(project_type="python")

        # Create a sample analysis result
        analysis_result = {
            "success": True,
            "framework": TestFramework.PYTEST.value,
            "summary": {"collected": 3, "passed": 2, "failed": 1},
            "failures": [
                {
                    "test_name": "test_func",
                    "error_type": "AssertionError",
                    "error_message": "assert 1 == 2",
                    "category": FailureCategory.ASSERTION_ERROR.value,
                    "severity": FailureSeverity.MEDIUM.value,
                    "confidence": 0.9,
                    "file_path": "file.py",
                    "line_number": 10
                }
            ],
            "recommendations": [
                {
                    "test_name": "test_func",
                    "category": FailureCategory.ASSERTION_ERROR.value,
                    "severity": FailureSeverity.MEDIUM.value,
                    "general_recommendations": [
                        "Review the test expectations and ensure they match the actual behavior"
                    ],
                    "specific_recommendations": []
                }
            ],
            "parsed_at": datetime.now().isoformat()
        }

        # Test JSON format
        json_report = analyzer.generate_report(analysis_result, format="json")
        assert isinstance(json_report, str)
        json_data = json.loads(json_report)
        assert json_data["success"] is True

        # Test HTML format
        html_report = analyzer.generate_report(analysis_result, format="html")
        assert isinstance(html_report, str)
        assert "<!DOCTYPE html>" in html_report
        assert "Test Failure Analysis Report" in html_report

        # Test Markdown format
        md_report = analyzer.generate_report(analysis_result, format="markdown")
        assert isinstance(md_report, str)
        assert "# Test Failure Analysis Report" in md_report

    def test_real_world_pytest_failure(self):
        """Test with a real-world pytest failure output."""
        analyzer = FailureAnalyzer(project_type="python")
        pytest_output = """
===== test session starts =====
platform darwin -- Python 3.10.0, pytest-8.3.4, pluggy-1.5.0
rootdir: /Users/ctavolazzi/Code/NovaSystem
collected 6 items

NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_basic_github_validation PASSED
NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_repository_metadata_extraction PASSED
NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_docker_container_creation FAILED
NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_repository_installation FAILED
NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_full_setup_flow FAILED
NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_failing_project FAILED

==================================== FAILURES ====================================
__________________________ test_docker_container_creation ___________________________

    def test_docker_container_creation():
        \"\"\"Test that a Docker container can be created for a valid repository.\"\"\"
        # Arrange
        validator = create_github_repo_validator()
        container_agent = create_docker_container_agent()

        # Act
        repo_result = validator.validate_repository(VALID_PYTHON_REPO_URL)
        container = container_agent.create_container(repo_result['repository_name'])

>       # Assert
>       assert container['status'] == 'created'
E       KeyError: 'status'

NovaSystem/backend/tests/integration/test_github_docker_flow.py:54: KeyError
____________________________ test_repository_installation ____________________________

    def test_repository_installation():
        \"\"\"Test that a repository can be installed in a Docker container.\"\"\"
        # Arrange
        validator = create_github_repo_validator()
        container_agent = create_docker_container_agent()

        # Act
        repo_result = validator.validate_repository(VALID_NODE_REPO_URL)
        container = container_agent.create_container(repo_result['repository_name'])
>       install_result = container_agent.install_repository(container['id'], repo_result)
E       KeyError: 'id'

NovaSystem/backend/tests/integration/test_github_docker_flow.py:72: KeyError
_______________________________ test_full_setup_flow _______________________________

    def test_full_setup_flow():
        \"\"\"Test the full flow from repository validation to test execution.\"\"\"
        # Arrange
        validator = create_github_repo_validator()
        container_agent = create_docker_container_agent()

        # Act - validate repository
        repo_result = validator.validate_repository(VALID_PYTHON_REPO_URL)
        assert repo_result['valid'] is True

        # Act - create container
        container = container_agent.create_container(repo_result['repository_name'])

        # Act - setup container based on project type
>       setup_result = container_agent.setup_container(container['id'], repo_result)
E       AttributeError: 'DockerContainerAgent' object has no attribute 'setup_container'

NovaSystem/backend/tests/integration/test_github_docker_flow.py:92: AttributeError
_______________________________ test_failing_project _______________________________

    def test_failing_project():
        \"\"\"Test handling of a failing project.\"\"\"
        # Arrange
        validator = create_github_repo_validator()
        container_agent = create_docker_container_agent()

        # Act - validate repository but it's invalid
        repo_result = validator.validate_repository(INVALID_REPO_URL)
        assert repo_result['valid'] is False

        # Should not proceed with container creation for invalid repos
        # But if we do, ensure proper error handling
        container = container_agent.create_container("invalid-repo")

>       setup_result = container_agent.setup_container(container['id'], repo_result)
E       AttributeError: 'DockerContainerAgent' object has no attribute 'setup_container'

NovaSystem/backend/tests/integration/test_github_docker_flow.py:113: AttributeError
=========================== short test summary info ============================
FAILED NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_docker_container_creation - KeyError: 'status'
FAILED NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_repository_installation - KeyError: 'id'
FAILED NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_full_setup_flow - AttributeError: 'DockerContainerAgent' object has no attribute 'setup_container'
FAILED NovaSystem/backend/tests/integration/test_github_docker_flow.py::test_failing_project - AttributeError: 'DockerContainerAgent' object has no attribute 'setup_container'
============================ 4 failed, 2 passed in 0.44s =====================
"""

        result = analyzer.analyze_test_output(pytest_output)

        # Verify overall results
        assert result["success"] is True
        assert result["framework"] == TestFramework.PYTEST.value
        assert len(result["failures"]) == 4

        # Verify failure categorization
        categories = {failure["category"] for failure in result["failures"]}
        # One should be categorized as import error (KeyError)
        assert FailureCategory.RUNTIME_ERROR.value in categories

        # Verify recommendations
        assert len(result["recommendations"]) == 4
        # Each failure should have recommendations
        for rec in result["recommendations"]:
            assert len(rec["general_recommendations"]) > 0