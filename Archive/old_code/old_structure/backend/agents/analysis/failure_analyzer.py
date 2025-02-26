"""
Failure Analysis module for NovaSystem.

This module provides functionality for analyzing test results from GitHub repositories,
categorizing failures, and generating recommendations.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum
from pathlib import Path
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)

class FailureCategory(Enum):
    """Enumeration of failure categories for test results."""
    SYNTAX_ERROR = "syntax_error"
    DEPENDENCY_ERROR = "dependency_error"
    ASSERTION_ERROR = "assertion_error"
    IMPORT_ERROR = "import_error"
    TIMEOUT_ERROR = "timeout_error"
    RUNTIME_ERROR = "runtime_error"
    PERMISSION_ERROR = "permission_error"
    RESOURCE_ERROR = "resource_error"
    UNKNOWN = "unknown"

class FailureSeverity(Enum):
    """Enumeration of failure severities."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class TestFramework(Enum):
    """Supported test frameworks for result parsing."""
    PYTEST = "pytest"
    JEST = "jest"
    JUNIT = "junit"
    NUNIT = "nunit"
    MOCHA = "mocha"
    GO_TEST = "go_test"
    UNKNOWN = "unknown"

class FailureAnalyzer:
    """
    Analyzes test results to categorize failures and provide recommendations.

    This class is responsible for parsing test output, categorizing failures,
    and generating reports with recommendations.
    """

    def __init__(self, project_type: str = "unknown"):
        """
        Initialize the failure analyzer.

        Args:
            project_type: The type of project (python, node, java, etc.)
        """
        self.project_type = project_type
        self.patterns = self._load_patterns()
        self.recommendations = self._load_recommendations()
        logger.info(f"Initialized FailureAnalyzer for project type: {project_type}")

    def analyze_test_output(self, test_output: str, framework: Union[TestFramework, str] = None) -> Dict[str, Any]:
        """
        Analyze test output to identify and categorize failures.

        Args:
            test_output: The raw test output
            framework: The test framework used (auto-detected if not provided)

        Returns:
            Dict with analysis results
        """
        if not test_output:
            return {
                "success": False,
                "error": "No test output provided",
                "failures": []
            }

        # Auto-detect framework if not provided
        if framework is None:
            framework = self._detect_framework(test_output)
        elif isinstance(framework, str):
            try:
                framework = TestFramework(framework)
            except ValueError:
                framework = TestFramework.UNKNOWN

        # Parse test results based on framework
        parse_result = self._parse_test_results(test_output, framework)

        # Categorize failures
        failures = self._categorize_failures(parse_result["failures"])

        # Generate recommendations
        recommendations = self._generate_recommendations(failures)

        return {
            "success": True,
            "framework": framework.value,
            "summary": parse_result["summary"],
            "failures": failures,
            "recommendations": recommendations,
            "parsed_at": datetime.now().isoformat()
        }

    def generate_report(self, analysis_result: Dict[str, Any], format: str = "json") -> str:
        """
        Generate a formatted report from analysis results.

        Args:
            analysis_result: The analysis result from analyze_test_output
            format: The output format (json, html, markdown)

        Returns:
            Formatted report as a string
        """
        if format == "json":
            return json.dumps(analysis_result, indent=2)
        elif format == "html":
            return self._generate_html_report(analysis_result)
        elif format == "markdown":
            return self._generate_markdown_report(analysis_result)
        else:
            return json.dumps(analysis_result, indent=2)

    def _detect_framework(self, test_output: str) -> TestFramework:
        """
        Detect the test framework from test output.

        Args:
            test_output: The raw test output

        Returns:
            Detected TestFramework
        """
        # Check for pytest patterns
        if "===== test session starts =====" in test_output or "collected" in test_output and "passed" in test_output:
            return TestFramework.PYTEST

        # Check for Jest patterns
        if "PASS" in test_output and ("Test Suites:" in test_output or "Jest" in test_output):
            return TestFramework.JEST

        # Check for JUnit patterns
        if "<testsuite" in test_output or ("Tests run:" in test_output and "Failures:" in test_output):
            return TestFramework.JUNIT

        # Check for Mocha patterns
        if "passing" in test_output and "failing" in test_output and "pending" in test_output:
            return TestFramework.MOCHA

        # Default to unknown
        return TestFramework.UNKNOWN

    def _parse_test_results(self, test_output: str, framework: TestFramework) -> Dict[str, Any]:
        """
        Parse test results based on the framework.

        Args:
            test_output: The raw test output
            framework: The test framework

        Returns:
            Dict with parsed results
        """
        if framework == TestFramework.PYTEST:
            return self._parse_pytest_results(test_output)
        elif framework == TestFramework.JEST:
            return self._parse_jest_results(test_output)
        elif framework == TestFramework.JUNIT:
            return self._parse_junit_results(test_output)
        elif framework == TestFramework.MOCHA:
            return self._parse_mocha_results(test_output)
        else:
            # Generic parsing for unknown frameworks
            return self._parse_generic_results(test_output)

    def _parse_pytest_results(self, test_output: str) -> Dict[str, Any]:
        """
        Parse pytest test results.

        Args:
            test_output: Raw pytest output

        Returns:
            Dict with parsed results
        """
        summary = {}
        failures = []

        # Extract summary information
        summary_match = re.search(r'=+ (.*?) in ([\d\.]+)s =+', test_output)
        if summary_match:
            summary["result"] = summary_match.group(1).strip()
            summary["duration"] = summary_match.group(2).strip()

        # Extract collected tests info
        collected_match = re.search(r'collected (\d+) items', test_output)
        if collected_match:
            summary["collected"] = int(collected_match.group(1))

        # Find failures
        failure_blocks = re.finditer(r'_{3,}\s+(.*?)\s+_{3,}(.*?)(?=_{3,}|\Z)', test_output, re.DOTALL)
        for block in failure_blocks:
            test_name = block.group(1).strip()
            failure_details = block.group(2).strip()

            # Extract file path and line number
            location_match = re.search(r'([\w\/\.]+):(\d+):', failure_details)
            file_path = location_match.group(1) if location_match else None
            line_number = int(location_match.group(2)) if location_match else None

            # Extract error type - Fix the regex pattern to better match error types
            error_match = re.search(r'([A-Za-z0-9_.]+(?:Error|Exception))(?::|$|\s)', failure_details)
            error_type = error_match.group(1) if error_match else "Unknown Error"

            # Extract error message
            error_message = ""
            if "E       " in failure_details:
                error_lines = re.findall(r'E\s+(.*)', failure_details)
                error_message = "\n".join(error_lines)
            else:
                error_message = failure_details

            failures.append({
                "test_name": test_name,
                "file_path": file_path,
                "line_number": line_number,
                "error_type": error_type,
                "error_message": error_message,
                "raw_details": failure_details
            })

        return {
            "summary": summary,
            "failures": failures
        }

    def _parse_jest_results(self, test_output: str) -> Dict[str, Any]:
        """
        Parse Jest test results.

        Args:
            test_output: Raw Jest output

        Returns:
            Dict with parsed results
        """
        summary = {}
        failures = []

        # Extract summary information
        test_suites_match = re.search(r'Test Suites:\s+(.*?)$', test_output, re.MULTILINE)
        if test_suites_match:
            summary["test_suites"] = test_suites_match.group(1).strip()

        tests_match = re.search(r'Tests:\s+(.*?)$', test_output, re.MULTILINE)
        if tests_match:
            summary["tests"] = tests_match.group(1).strip()

        time_match = re.search(r'Time:\s+(.*?)$', test_output, re.MULTILINE)
        if time_match:
            summary["time"] = time_match.group(1).strip()

        # Find failures
        failure_blocks = re.finditer(r'● (.*?)\n+([-\s\w\d\./]+:\d+:\d+\)?\s*\n+)(.*?)(?=●|\n\n\n|\Z)', test_output, re.DOTALL)
        for block in failure_blocks:
            test_name = block.group(1).strip()
            location = block.group(2).strip()
            failure_details = block.group(3).strip()

            # Extract file path and line number
            location_match = re.search(r'([\w\/\.-]+):(\d+):', location)
            file_path = location_match.group(1) if location_match else None
            line_number = int(location_match.group(2)) if location_match else None

            failures.append({
                "test_name": test_name,
                "file_path": file_path,
                "line_number": line_number,
                "error_type": "Jest Error",
                "error_message": failure_details,
                "raw_details": f"{location}\n{failure_details}"
            })

        return {
            "summary": summary,
            "failures": failures
        }

    def _parse_junit_results(self, test_output: str) -> Dict[str, Any]:
        """
        Parse JUnit test results.

        Args:
            test_output: Raw JUnit output

        Returns:
            Dict with parsed results
        """
        # Implementation for JUnit XML format
        # For simplicity, returning a placeholder
        return {
            "summary": {
                "result": "Parsed JUnit format"
            },
            "failures": []
        }

    def _parse_mocha_results(self, test_output: str) -> Dict[str, Any]:
        """
        Parse Mocha test results.

        Args:
            test_output: Raw Mocha output

        Returns:
            Dict with parsed results
        """
        # Implementation for Mocha format
        # For simplicity, returning a placeholder
        return {
            "summary": {
                "result": "Parsed Mocha format"
            },
            "failures": []
        }

    def _parse_generic_results(self, test_output: str) -> Dict[str, Any]:
        """
        Generic parser for unknown test frameworks.

        Args:
            test_output: Raw test output

        Returns:
            Dict with parsed results
        """
        failures = []

        # Look for common error patterns
        error_matches = re.finditer(r'(?:error|Error|ERROR|FAIL|Fail|fail)(?:ed)?:?\s*(.*?)(?:\n|$)', test_output, re.MULTILINE)
        for match in error_matches:
            error_message = match.group(1).strip()
            if error_message:
                failures.append({
                    "test_name": "Unknown Test",
                    "file_path": None,
                    "line_number": None,
                    "error_type": "Unknown Error",
                    "error_message": error_message,
                    "raw_details": error_message
                })

        return {
            "summary": {
                "result": "Generic parsing",
                "passed": len(failures) == 0
            },
            "failures": failures
        }

    def _categorize_failures(self, failures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize failures based on error type and message.

        Args:
            failures: List of failure dictionaries

        Returns:
            List of failures with added categories and severity
        """
        categorized_failures = []

        for failure in failures:
            category = FailureCategory.UNKNOWN
            severity = FailureSeverity.MEDIUM
            confidence = 0.5

            error_type = failure.get("error_type", "")
            error_message = failure.get("error_message", "")

            # Check for syntax errors
            if "SyntaxError" in error_type or "syntax error" in error_message.lower():
                category = FailureCategory.SYNTAX_ERROR
                severity = FailureSeverity.HIGH
                confidence = 0.9

            # Check for import errors
            elif "ImportError" in error_type or "ModuleNotFoundError" in error_type:
                category = FailureCategory.IMPORT_ERROR
                severity = FailureSeverity.HIGH
                confidence = 0.9

            # Check for dependency errors
            elif "DependencyError" in error_type or "requirement" in error_message.lower() or "dependency" in error_message.lower():
                category = FailureCategory.DEPENDENCY_ERROR
                severity = FailureSeverity.HIGH
                confidence = 0.8

            # Check for assertion errors
            elif "AssertionError" in error_type or "assert" in error_message.lower():
                category = FailureCategory.ASSERTION_ERROR
                severity = FailureSeverity.MEDIUM
                confidence = 0.9

            # Check for timeout errors
            elif "TimeoutError" in error_type or "timed out" in error_message.lower():
                category = FailureCategory.TIMEOUT_ERROR
                severity = FailureSeverity.MEDIUM
                confidence = 0.8

            # Check for permission errors
            elif "PermissionError" in error_type or "permission denied" in error_message.lower():
                category = FailureCategory.PERMISSION_ERROR
                severity = FailureSeverity.HIGH
                confidence = 0.9

            # Check for resource errors
            elif "ResourceError" in error_type or "memory" in error_message.lower() or "disk space" in error_message.lower():
                category = FailureCategory.RESOURCE_ERROR
                severity = FailureSeverity.CRITICAL
                confidence = 0.8

            # Default to runtime error if we can't categorize more specifically
            elif "Error" in error_type or "Exception" in error_type:
                category = FailureCategory.RUNTIME_ERROR
                severity = FailureSeverity.MEDIUM
                confidence = 0.7

            # Apply project-specific patterns
            if self.project_type in self.patterns:
                for pattern_info in self.patterns[self.project_type]:
                    if re.search(pattern_info["pattern"], error_message, re.IGNORECASE):
                        category = FailureCategory(pattern_info["category"])
                        severity = FailureSeverity(pattern_info["severity"])
                        confidence = pattern_info["confidence"]
                        break

            failure_copy = failure.copy()
            failure_copy.update({
                "category": category.value,
                "severity": severity.value,
                "confidence": confidence
            })
            categorized_failures.append(failure_copy)

        return categorized_failures

    def _generate_recommendations(self, failures: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on categorized failures.

        Args:
            failures: List of categorized failures

        Returns:
            List of recommendations
        """
        recommendations = []

        for failure in failures:
            category = failure.get("category")

            # Get general recommendations for this category
            general_recs = self._get_category_recommendations(category)

            # Get project-specific recommendations
            specific_recs = self._get_project_specific_recommendations(
                category,
                failure.get("error_type", ""),
                failure.get("error_message", "")
            )

            recommendations.append({
                "test_name": failure.get("test_name", "Unknown Test"),
                "category": category,
                "severity": failure.get("severity", FailureSeverity.MEDIUM.value),
                "general_recommendations": general_recs,
                "specific_recommendations": specific_recs
            })

        return recommendations

    def _get_category_recommendations(self, category: str) -> List[str]:
        """
        Get general recommendations for a failure category.

        Args:
            category: The failure category

        Returns:
            List of recommendation strings
        """
        # Default recommendations by category
        category_recs = {
            FailureCategory.SYNTAX_ERROR.value: [
                "Check for syntax errors in the indicated file and line",
                "Validate the code against the language's syntax rules",
                "Use a linter to identify and fix syntax issues"
            ],
            FailureCategory.IMPORT_ERROR.value: [
                "Verify that the imported module is installed",
                "Check that the module path is correct",
                "Ensure the module is compatible with the current Python/Node.js version"
            ],
            FailureCategory.DEPENDENCY_ERROR.value: [
                "Install missing dependencies using the appropriate package manager",
                "Check for version conflicts between dependencies",
                "Verify that the dependency is compatible with the project"
            ],
            FailureCategory.ASSERTION_ERROR.value: [
                "Review the test expectations and ensure they match the actual behavior",
                "Check for changes in the tested code that might affect the expected outcome",
                "Verify that the test data and environment are correctly set up"
            ],
            FailureCategory.TIMEOUT_ERROR.value: [
                "Check for performance issues or infinite loops in the code",
                "Increase the test timeout if the operation legitimately takes longer",
                "Consider optimizing the code or breaking it into smaller testable units"
            ],
            FailureCategory.PERMISSION_ERROR.value: [
                "Verify that the process has the necessary permissions to access files or resources",
                "Check file and directory permissions in the test environment",
                "Consider running tests with appropriate privileges"
            ],
            FailureCategory.RESOURCE_ERROR.value: [
                "Check for memory leaks or excessive resource usage",
                "Ensure sufficient resources are available in the test environment",
                "Consider optimizing resource usage in the code"
            ],
            FailureCategory.RUNTIME_ERROR.value: [
                "Debug the application to identify the specific cause of the error",
                "Add error handling for edge cases",
                "Review the logic around the error location"
            ],
            FailureCategory.UNKNOWN.value: [
                "Review the error message and stack trace to identify the issue",
                "Check for common issues like typos, missing files, or configuration problems",
                "Consider adding more detailed error logging to help diagnose the issue"
            ]
        }

        return category_recs.get(category, category_recs[FailureCategory.UNKNOWN.value])

    def _get_project_specific_recommendations(self, category: str, error_type: str, error_message: str) -> List[str]:
        """
        Get project-specific recommendations based on the error details.

        Args:
            category: The failure category
            error_type: The error type
            error_message: The error message

        Returns:
            List of recommendation strings
        """
        specific_recs = []

        # Look up recommendations from the loaded patterns
        if self.project_type in self.recommendations:
            for rec_info in self.recommendations[self.project_type]:
                if category == rec_info.get("category") and re.search(rec_info.get("pattern", ""), error_message, re.IGNORECASE):
                    specific_recs.extend(rec_info.get("recommendations", []))

        # If no specific recommendations were found, try to generate some
        if not specific_recs:
            if "module" in error_message.lower() and self.project_type == "python":
                module_match = re.search(r'No module named [\'"]([^\'"]+)[\'"]', error_message)
                if module_match:
                    module_name = module_match.group(1)
                    specific_recs.append("Install the missing module: pip install {}".format(module_name))

            elif "npm" in error_message.lower() and self.project_type == "node":
                package_match = re.search(r'Cannot find module [\'"]([^\'"]+)[\'"]', error_message)
                if package_match:
                    package_name = package_match.group(1)
                    specific_recs.append("Install the missing package: npm install {}".format(package_name))

        return specific_recs

    def _generate_html_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate an HTML report from analysis results.

        Args:
            analysis_result: The analysis result

        Returns:
            HTML report as a string
        """
        # Build HTML report with separate style section to avoid formatting conflicts
        style = """
<style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    h1 { color: #333; }
    .summary { background: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 20px; }
    .failure { border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
    .critical { border-left: 5px solid #d9534f; }
    .high { border-left: 5px solid #f0ad4e; }
    .medium { border-left: 5px solid #5bc0de; }
    .low { border-left: 5px solid #5cb85c; }
    .info { border-left: 5px solid #337ab7; }
    .recommendations { background: #e8f4f8; padding: 10px; border-radius: 5px; }
</style>
"""

        # Main HTML template without CSS in the format string
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Failure Analysis Report</title>
    {style}
</head>
<body>
    <h1>Test Failure Analysis Report</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Framework:</strong> {framework}</p>
        <p><strong>Analyzed At:</strong> {analyzed_at}</p>
        <p><strong>Failures:</strong> {failure_count}</p>
    </div>
""".format(
            style=style,
            framework=analysis_result.get("framework", "Unknown"),
            analyzed_at=analysis_result.get("parsed_at", "Unknown"),
            failure_count=len(analysis_result.get("failures", []))
        )

        # Add failures
        if analysis_result.get("failures"):
            html += "<h2>Failures</h2>"

            for i, failure in enumerate(analysis_result.get("failures", [])):
                severity_class = failure.get("severity", "medium")
                html += """
<div class="failure {severity_class}">
    <h3>Failure #{i}: {test_name}</h3>
    <p><strong>File:</strong> {file_path}:{line_number}</p>
    <p><strong>Error Type:</strong> {error_type}</p>
    <p><strong>Category:</strong> {category} (Confidence: {confidence:.1f})</p>
    <p><strong>Message:</strong> {message}</p>
</div>
""".format(
                    severity_class=severity_class,
                    i=i+1,
                    test_name=failure.get("test_name", "Unknown Test"),
                    file_path=failure.get("file_path", "Unknown"),
                    line_number=failure.get("line_number", "?"),
                    error_type=failure.get("error_type", "Unknown Error"),
                    category=failure.get("category", "unknown"),
                    confidence=failure.get("confidence", 0.0),
                    message=failure.get("error_message", "No message")
                )

        # Add recommendations
        if analysis_result.get("recommendations"):
            html += "<h2>Recommendations</h2>"

            for i, rec in enumerate(analysis_result.get("recommendations", [])):
                rec_html = """
<div class="recommendations">
    <h3>For: {test_name}</h3>
    <h4>General Recommendations:</h4>
    <ul>
""".format(test_name=rec.get("test_name", "Unknown Test"))

                # Add general recommendations
                for item in rec.get("general_recommendations", []):
                    rec_html += "<li>{}</li>".format(item)

                rec_html += "</ul>"

                # Add specific recommendations if any
                if rec.get("specific_recommendations"):
                    rec_html += "<h4>Specific Recommendations:</h4><ul>"
                    for item in rec.get("specific_recommendations", []):
                        rec_html += "<li>{}</li>".format(item)
                    rec_html += "</ul>"

                rec_html += "</div>"
                html += rec_html

        html += """
</body>
</html>
"""

        return html

    def _generate_markdown_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate a Markdown report from analysis results.

        Args:
            analysis_result: The analysis result

        Returns:
            Markdown report as a string
        """
        # Simple Markdown report implementation
        markdown = """
# Test Failure Analysis Report

## Summary

- **Framework:** {framework}
- **Analyzed At:** {analyzed_at}
- **Failures:** {failure_count}

## Failures
""".format(
            framework=analysis_result.get("framework", "Unknown"),
            analyzed_at=analysis_result.get("parsed_at", "Unknown"),
            failure_count=len(analysis_result.get("failures", []))
        )

        # Add failures
        for i, failure in enumerate(analysis_result.get("failures", [])):
            markdown += """
### Failure #{i}: {test_name}

- **File:** {file_path}:{line_number}
- **Error Type:** {error_type}
- **Category:** {category} (Confidence: {confidence:.1f})
- **Severity:** {severity}
- **Message:** {message}
""".format(
                i=i+1,
                test_name=failure.get("test_name", "Unknown Test"),
                file_path=failure.get("file_path", "Unknown"),
                line_number=failure.get("line_number", "?"),
                error_type=failure.get("error_type", "Unknown Error"),
                category=failure.get("category", "unknown"),
                confidence=failure.get("confidence", 0.0),
                severity=failure.get("severity", "medium"),
                message=failure.get("error_message", "No message")
            )

        # Add recommendations
        markdown += """
## Recommendations
"""

        for i, rec in enumerate(analysis_result.get("recommendations", [])):
            markdown += """
### For: {test_name}

#### General Recommendations:

""".format(test_name=rec.get("test_name", "Unknown Test"))

            # Add general recommendations
            for item in rec.get("general_recommendations", []):
                markdown += "- {}\n".format(item)

            # Add specific recommendations if any
            if rec.get("specific_recommendations"):
                markdown += """
#### Specific Recommendations:

"""
                for item in rec.get("specific_recommendations", []):
                    markdown += "- {}\n".format(item)

        return markdown

    def _load_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load failure pattern definitions for different project types.

        Returns:
            Dict of project types with their failure patterns
        """
        # In a real implementation, these might be loaded from a file or database
        return {
            "python": [
                {
                    "pattern": r"No module named",
                    "category": FailureCategory.IMPORT_ERROR.value,
                    "severity": FailureSeverity.HIGH.value,
                    "confidence": 0.9
                },
                {
                    "pattern": r"IndentationError",
                    "category": FailureCategory.SYNTAX_ERROR.value,
                    "severity": FailureSeverity.HIGH.value,
                    "confidence": 0.95
                }
            ],
            "node": [
                {
                    "pattern": r"Cannot find module",
                    "category": FailureCategory.IMPORT_ERROR.value,
                    "severity": FailureSeverity.HIGH.value,
                    "confidence": 0.9
                },
                {
                    "pattern": r"SyntaxError: Unexpected token",
                    "category": FailureCategory.SYNTAX_ERROR.value,
                    "severity": FailureSeverity.HIGH.value,
                    "confidence": 0.95
                }
            ],
            "java": [
                {
                    "pattern": r"ClassNotFoundException",
                    "category": FailureCategory.IMPORT_ERROR.value,
                    "severity": FailureSeverity.HIGH.value,
                    "confidence": 0.9
                },
                {
                    "pattern": r"OutOfMemoryError",
                    "category": FailureCategory.RESOURCE_ERROR.value,
                    "severity": FailureSeverity.CRITICAL.value,
                    "confidence": 0.95
                }
            ]
        }

    def _load_recommendations(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load recommendation definitions for different project types.

        Returns:
            Dict of project types with their recommendations
        """
        # In a real implementation, these might be loaded from a file or database
        return {
            "python": [
                {
                    "category": FailureCategory.IMPORT_ERROR.value,
                    "pattern": r"No module named '(\w+)'",
                    "recommendations": [
                        "Run 'pip install {match_1}'",
                        "Check if the module name is spelled correctly",
                        "Verify that the module is compatible with your Python version"
                    ]
                },
                {
                    "category": FailureCategory.SYNTAX_ERROR.value,
                    "pattern": r"IndentationError",
                    "recommendations": [
                        "Fix the indentation in the indicated file",
                        "Use a consistent indentation style (spaces or tabs)",
                        "Configure your editor to show whitespace characters"
                    ]
                }
            ],
            "node": [
                {
                    "category": FailureCategory.IMPORT_ERROR.value,
                    "pattern": r"Cannot find module '(\w+)'",
                    "recommendations": [
                        "Run 'npm install {match_1}'",
                        "Check if the package name is spelled correctly",
                        "Verify that the package is listed in package.json"
                    ]
                }
            ],
            "java": [
                {
                    "category": FailureCategory.RESOURCE_ERROR.value,
                    "pattern": r"OutOfMemoryError",
                    "recommendations": [
                        "Increase the JVM heap size using -Xmx option",
                        "Check for memory leaks in the application",
                        "Review large object allocations in the code"
                    ]
                }
            ]
        }