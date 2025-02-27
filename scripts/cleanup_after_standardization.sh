#!/bin/bash
# NovaSystem Cleanup After Standardization

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Cleanup After Standardization${NC}"
echo "----------------------------------------"

# Get confirmation
echo -e "${RED}WARNING: This script will remove redundant nested directories.${NC}"
echo -e "Make sure you have verified that all tests pass before running this script."
read -p "Are you sure you want to proceed? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Operation cancelled."
    exit 1
fi

echo -e "\n${YELLOW}Cleaning up redundant nested directories...${NC}"

# Remove nested novasystem directory
if [ -d "novasystem/novasystem" ]; then
    echo "Removing nested novasystem/novasystem directory..."
    rm -rf novasystem/novasystem
    echo -e "${GREEN}Removed novasystem/novasystem${NC}"
fi

# Remove nested tests directory
if [ -d "novasystem/tests" ]; then
    echo "Removing nested novasystem/tests directory..."
    rm -rf novasystem/tests
    echo -e "${GREEN}Removed novasystem/tests${NC}"
fi

# Clean up other unnecessary files
if [ -d "novasystem/.pytest_cache" ]; then
    echo "Removing novasystem/.pytest_cache..."
    rm -rf novasystem/.pytest_cache
    echo -e "${GREEN}Removed novasystem/.pytest_cache${NC}"
fi

if [ -d "novasystem/novasystem.egg-info" ]; then
    echo "Removing novasystem/novasystem.egg-info..."
    rm -rf novasystem/novasystem.egg-info
    echo -e "${GREEN}Removed novasystem/novasystem.egg-info${NC}"
fi

if [ -f "novasystem/pyproject.toml" ]; then
    echo "Removing redundant novasystem/pyproject.toml..."
    rm novasystem/pyproject.toml
    echo -e "${GREEN}Removed novasystem/pyproject.toml${NC}"
fi

echo -e "\n${GREEN}Cleanup complete!${NC}"
echo -e "\n${YELLOW}Final steps:${NC}"
echo -e "1. Verify that imports still work by running tests: ./scripts/run_tests.sh"
echo -e "2. If everything is working correctly, you may want to remove the original NovaSystem directory"
echo -e "   but this is optional and should only be done when you're 100% confident in the new structure."