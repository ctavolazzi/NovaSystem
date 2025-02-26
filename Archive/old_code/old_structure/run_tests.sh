#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}"
echo "==============================================="
echo "     🧪 NovaSystem Test Runner 🧪"
echo "==============================================="
echo -e "${NC}"

# Navigate to project root
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${BLUE}Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Installing required packages..."
    pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-timeout
fi

# Create necessary directories for test artifacts
mkdir -p .build/coverage
mkdir -p .build/reports
mkdir -p .build/logs

# Get current timestamp for report naming
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Set Python path to include project root for imports
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Run pytest with coverage
echo "Running tests with coverage..."
python -m pytest backend/tests/ \
    -v \
    --cov=backend \
    --cov-report=term \
    --cov-report=html:.build/coverage \
    | tee .build/reports/test_report_${TIMESTAMP}.txt

# Print test summary
echo ""
echo "Test run complete!"
echo "Coverage report saved to .build/coverage/"
echo "Test report saved to .build/reports/test_report_${TIMESTAMP}.txt"

# Helpful commands
echo ""
echo "Helpful commands:"
echo "Run specific test: python -m pytest backend/tests/path/to/test.py -v"
echo "Run with more output: python -m pytest backend/tests/ -vv"
echo "Run with specific markers: python -m pytest backend/tests/ -m 'not slow'"