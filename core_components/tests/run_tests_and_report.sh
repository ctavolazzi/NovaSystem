#!/bin/bash

# Script to run pytest tests, generate an HTML test report, and measure coverage.
# !!! This script MUST be run from the PROJECT ROOT directory !!!

# Ensure the script exits if any command fails
# set -e # Removed to allow script to continue and open report even on test failure

# --- Configuration ---
# Directory containing the code to measure coverage for
COVERAGE_SOURCE="core_components"
# Test directories to run
TEST_DIRS="tests/ core_components/"
# Path for the HTML test report
TEST_REPORT_DIR="core_components/tests/results"
TEST_REPORT_FILE="${TEST_REPORT_DIR}/test_report.html"
# Path for the HTML coverage report
COVERAGE_REPORT_DIR="core_components/tests/coverage_report"

# --- Setup ---
# Ensure report directories exist
mkdir -p "$TEST_REPORT_DIR"
mkdir -p "$COVERAGE_REPORT_DIR"

# --- Execution ---
echo "Running tests from: ${TEST_DIRS}"
echo "Measuring coverage for: ${COVERAGE_SOURCE}"
echo "Generating HTML test report at: ${TEST_REPORT_FILE}"
echo "Generating HTML coverage report at: ${COVERAGE_REPORT_DIR}"
echo "Displaying coverage summary in terminal."
echo "..."

# Explicitly add the current directory (project root) to PYTHONPATH
export PYTHONPATH=".:${PYTHONPATH}"
echo "PYTHONPATH set to: $PYTHONPATH"

# Run pytest with coverage and HTML reporting
# NOTE: Ensure 'pytest-html' and 'pytest-cov' are installed.
pytest -v \
       ${TEST_DIRS} \
       --cov=${COVERAGE_SOURCE} \
       --cov-report=term-missing \
       --cov-report=html:"${COVERAGE_REPORT_DIR}" \
       --html="$TEST_REPORT_FILE" \
       --self-contained-html

# Capture the exit code of pytest
PYTEST_EXIT_CODE=$?

echo "..."
echo "Pytest exited with code: ${PYTEST_EXIT_CODE}"
if [ $PYTEST_EXIT_CODE -ne 0 ] && [ $PYTEST_EXIT_CODE -ne 5 ]; then
    # Exit code 5 means no tests were collected, which might be ok in some cases
    echo "Warning: Pytest reported errors or failures!"
fi
echo "Test run and coverage analysis complete."
echo "HTML Test Report: ${TEST_REPORT_FILE}"
echo "HTML Coverage Report: ${COVERAGE_REPORT_DIR}/index.html"

# Attempt to open the coverage report
echo "Attempting to open coverage report..."
open "${COVERAGE_REPORT_DIR}/index.html" # Open Coverage Report on macOS

# Optional: Open other reports or adjust for other OS
# open "$TEST_REPORT_FILE"  # macOS (Test Report)
# xdg-open "${COVERAGE_REPORT_DIR}/index.html" # Linux
# start "" "${COVERAGE_REPORT_DIR}\index.html" # Windows (Coverage)

exit $PYTEST_EXIT_CODE # Exit script with the pytest exit code