#!/bin/bash
# NovaSystem Simple Standardization Script

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Simple Standardization${NC}"
echo "--------------------------------"

# Create the novasystem package directory at the root
echo -e "\n${YELLOW}1. Creating novasystem package at root...${NC}"
mkdir -p novasystem

# Copy all Python files from NovaSystem to novasystem
echo "Copying Python files to novasystem/"
cp -n NovaSystem/*.py novasystem/
cp -n NovaSystem/github_docker_integration.md novasystem/

# Ensure we have __init__.py
if [ ! -f "novasystem/__init__.py" ]; then
    echo "Creating __init__.py"
    cp NovaSystem/__init__.py novasystem/
fi

# Verify the novasystem package structure
echo -e "\n${YELLOW}2. Verifying package structure...${NC}"
if [ -f "novasystem/__init__.py" ] && [ -f "novasystem/cli.py" ]; then
    echo -e "${GREEN}Package structure created successfully!${NC}"
else
    echo -e "${RED}Failed to create proper package structure!${NC}"
    exit 1
fi

# Create pyproject.toml at the root if not already present
if [ ! -f "pyproject.toml" ] && [ -f "NovaSystem/pyproject.toml" ]; then
    echo -e "\n${YELLOW}3. Copying pyproject.toml to root...${NC}"
    cp NovaSystem/pyproject.toml ./
    echo -e "${GREEN}pyproject.toml copied to root${NC}"
fi

# Make sure we have a tests directory
mkdir -p tests

# Copy tests from NovaSystem/tests to tests if they exist
if [ -d "NovaSystem/tests" ] && [ "$(ls -A NovaSystem/tests)" ]; then
    echo -e "\n${YELLOW}4. Copying tests to root tests/ directory...${NC}"
    cp -rn NovaSystem/tests/* tests/
    echo -e "${GREEN}Tests copied to tests/ directory${NC}"
fi

# Fix import paths in tests
echo -e "\n${YELLOW}5. Updating import paths in tests...${NC}"
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.novasystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.novasystem/import novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.NovaSystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.NovaSystem/import novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem/import novasystem/g' || true

echo -e "\n${GREEN}Standardization complete!${NC}"
echo -e "\n${YELLOW}Final steps:${NC}"
echo -e "1. Run the sanity check to verify the structure: python scripts/test_sanity_check.py"
echo -e "2. Run the tests to confirm everything works: ./scripts/run_tests.sh"
echo -e "3. If everything works, you may safely use the new structure"