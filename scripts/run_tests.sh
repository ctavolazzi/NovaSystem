#!/bin/bash
# Smart test runner for NovaSystem
# This script runs sanity checks before executing tests

set -e  # Exit immediately if a command exits with a non-zero status

# Define colors for terminal output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Test Runner${NC}"
echo "---------------------"

# First make sure we're in the project root
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)

# In the standardized structure, tests should be in the root tests/ directory
TEST_DIR="tests/"

# Verify the tests directory exists
if [ ! -d "${ROOT_DIR}/${TEST_DIR}" ]; then
    echo -e "${RED}Error: Tests directory not found at ${ROOT_DIR}/${TEST_DIR}${NC}"
    echo -e "If you haven't standardized the project yet, run: ./scripts/standardize_project.sh"
    exit 1
fi

echo "Using test directory: ${TEST_DIR}"

# Run the sanity check script
echo -e "\n${YELLOW}Running sanity checks...${NC}"
python scripts/test_sanity_check.py || true  # Continue even if sanity checks fail for now

# Parse command line options
COVERAGE=0
SPECIFIC_TESTS=""
PYTEST_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --cov|--coverage)
            COVERAGE=1
            shift
            ;;
        --file=*)
            SPECIFIC_TESTS="${1#*=}"
            shift
            ;;
        *)
            PYTEST_ARGS="$PYTEST_ARGS $1"
            shift
            ;;
    esac
done

# Build the pytest command
PYTEST_CMD="python -m pytest"

# Add coverage if requested
if [ $COVERAGE -eq 1 ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=novasystem --cov-report=term"
fi

# Add specific test file if provided
if [ ! -z "$SPECIFIC_TESTS" ]; then
    PYTEST_CMD="$PYTEST_CMD $SPECIFIC_TESTS"
else
    PYTEST_CMD="$PYTEST_CMD $TEST_DIR"
fi

# Add any additional pytest arguments
if [ ! -z "$PYTEST_ARGS" ]; then
    PYTEST_CMD="$PYTEST_CMD $PYTEST_ARGS"
fi

# Run the tests
echo -e "\n${YELLOW}Running tests...${NC}"
echo "Command: $PYTEST_CMD"
eval $PYTEST_CMD
TEST_RESULT=$?

# Report results
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed successfully!${NC}"
else
    echo -e "\n${RED}Tests failed with exit code $TEST_RESULT${NC}"
fi

exit $TEST_RESULT