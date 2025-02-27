#!/bin/bash
# NovaSystem Forced Standardization Script

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Forced Standardization${NC}"
echo "--------------------------------"

# Force create the novasystem package directory at the root
echo -e "\n${YELLOW}1. Forcefully creating novasystem package at root...${NC}"

# Remove existing directory if it exists (to avoid confusion)
if [ -d "novasystem" ]; then
    echo "Removing existing novasystem directory..."
    rm -rf novasystem
fi

# Create fresh directory
mkdir -p novasystem
echo "Created fresh novasystem directory"

# Copy files (using force flag to ensure they're copied)
echo "Copying Python files to novasystem/"
cp -f NovaSystem/*.py novasystem/ 2>/dev/null || true
cp -f NovaSystem/github_docker_integration.md novasystem/ 2>/dev/null || true

# Verify files were actually copied
echo -e "\n${YELLOW}2. Verifying package structure...${NC}"
ls -la novasystem/
if [ -f "novasystem/__init__.py" ] && [ -f "novasystem/cli.py" ]; then
    echo -e "${GREEN}Package structure created successfully!${NC}"
else
    echo -e "${RED}Failed to create proper package structure!${NC}"

    # Try the capitalized directory as fallback
    echo "Trying files from NovaSystem/NovaSystem/"
    cp -f NovaSystem/NovaSystem/*.py novasystem/ 2>/dev/null || true

    # Try the lowercase directory as another fallback
    echo "Trying files from NovaSystem/novasystem/"
    cp -f NovaSystem/novasystem/*.py novasystem/ 2>/dev/null || true

    # Check again
    if [ -f "novasystem/__init__.py" ] && [ -f "novasystem/cli.py" ]; then
        echo -e "${GREEN}Package structure created successfully on second attempt!${NC}"
    else
        echo -e "${RED}Failed to create proper package structure after multiple attempts!${NC}"
        exit 1
    fi
fi

# Create pyproject.toml at the root if not already present
if [ ! -f "pyproject.toml" ] && [ -f "NovaSystem/pyproject.toml" ]; then
    echo -e "\n${YELLOW}3. Copying pyproject.toml to root...${NC}"
    cp NovaSystem/pyproject.toml ./
    echo -e "${GREEN}pyproject.toml copied to root${NC}"
fi

# Force create a tests directory
echo -e "\n${YELLOW}4. Creating tests directory...${NC}"
mkdir -p tests

# Copy tests from NovaSystem/tests to tests if they exist
if [ -d "NovaSystem/tests" ]; then
    echo "Copying tests from NovaSystem/tests/"
    cp -rf NovaSystem/tests/* tests/ 2>/dev/null || true
fi

# Fix import paths in tests
echo -e "\n${YELLOW}5. Updating import paths in tests...${NC}"
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.novasystem/from novasystem/g' 2>/dev/null || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.novasystem/import novasystem/g' 2>/dev/null || true
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.NovaSystem/from novasystem/g' 2>/dev/null || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.NovaSystem/import novasystem/g' 2>/dev/null || true
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem/from novasystem/g' 2>/dev/null || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem/import novasystem/g' 2>/dev/null || true

echo -e "\n${GREEN}Standardization complete!${NC}"
echo -e "Run the sanity check to verify the structure: python scripts/test_sanity_check.py"