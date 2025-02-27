#!/bin/bash
# NovaSystem Project Standardization Script (Fixed Version)

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Project Standardization (Fixed Version)${NC}"
echo "----------------------------------------------"

# Create backup first
echo -e "\n${YELLOW}1. Creating backup...${NC}"
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)
BACKUP_DIR="${ROOT_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
echo "Creating backup at ${BACKUP_DIR}..."

# Explicitly list directories to backup - EXCLUDE any backup_* directories
for item in $(ls -A | grep -v "^\." | grep -v "^backup_" | grep -v "venv" | grep -v "node_modules"); do
    if [ -d "$item" ] || [ -f "$item" ]; then
        echo "Backing up $item..."
        cp -r "$item" "${BACKUP_DIR}/"
    fi
done
echo -e "${GREEN}Backup created at $BACKUP_DIR${NC}"

# Standardize package structure
echo -e "\n${YELLOW}2. Standardizing package structure...${NC}"

# Create standard directory structure if not exist
mkdir -p novasystem
mkdir -p tests

# Find the actual package code - check multiple possible locations
echo "Looking for package code..."
FOUND_CODE=0

# Check if files exist directly in NovaSystem/
if [ -f "NovaSystem/cli.py" ] || [ -f "NovaSystem/nova.py" ]; then
    echo "Found package code in NovaSystem/"
    cp -rn NovaSystem/*.py novasystem/
    FOUND_CODE=1
fi

# Check if files exist in NovaSystem/NovaSystem/
if [ -d "NovaSystem/NovaSystem" ] && [ -f "NovaSystem/NovaSystem/cli.py" ]; then
    echo "Found package code in NovaSystem/NovaSystem/"
    cp -rn NovaSystem/NovaSystem/*.py novasystem/
    FOUND_CODE=1
fi

# Check if files exist in NovaSystem/novasystem/
if [ -d "NovaSystem/novasystem" ] && [ -f "NovaSystem/novasystem/cli.py" ]; then
    echo "Found package code in NovaSystem/novasystem/"
    cp -rn NovaSystem/novasystem/*.py novasystem/
    FOUND_CODE=1
fi

if [ $FOUND_CODE -eq 0 ]; then
    echo -e "${RED}Couldn't find package code in expected locations!${NC}"
    echo "Please specify the location manually."
    exit 1
else
    echo -e "${GREEN}Package code moved to standard location${NC}"
fi

# Move tests to standard location - check multiple possible locations
echo "Looking for tests..."
FOUND_TESTS=0

# Check in NovaSystem/tests/
if [ -d "NovaSystem/tests" ]; then
    echo "Found tests in NovaSystem/tests/"
    cp -rn NovaSystem/tests/* tests/
    FOUND_TESTS=1
fi

# Check in NovaSystem/NovaSystem/tests/
if [ -d "NovaSystem/NovaSystem/tests" ]; then
    echo "Found tests in NovaSystem/NovaSystem/tests/"
    cp -rn NovaSystem/NovaSystem/tests/* tests/
    FOUND_TESTS=1
fi

if [ $FOUND_TESTS -eq 1 ]; then
    echo -e "${GREEN}Tests moved to standard location${NC}"
else
    echo -e "${YELLOW}No tests found in expected locations.${NC}"
fi

# Copy pyproject.toml to root if needed
if [ ! -f "pyproject.toml" ]; then
    if [ -f "NovaSystem/pyproject.toml" ]; then
        echo "Moving pyproject.toml from NovaSystem/..."
        cp NovaSystem/pyproject.toml ./
        echo -e "${GREEN}pyproject.toml moved to root${NC}"
    elif [ -f "NovaSystem/NovaSystem/pyproject.toml" ]; then
        echo "Moving pyproject.toml from NovaSystem/NovaSystem/..."
        cp NovaSystem/NovaSystem/pyproject.toml ./
        echo -e "${GREEN}pyproject.toml moved to root${NC}"
    else
        echo -e "${YELLOW}No pyproject.toml found in expected locations.${NC}"
    fi
fi

# Update import paths in test files
echo -e "\n${YELLOW}3. Updating import paths in tests...${NC}"
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.novasystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.novasystem/import novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.NovaSystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.NovaSystem/import novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem/import novasystem/g' || true

# Create a proper __init__.py if it doesn't exist
if [ ! -f "novasystem/__init__.py" ]; then
    echo "Creating novasystem/__init__.py..."
    echo "# NovaSystem package" > novasystem/__init__.py
fi

# Verify and update paths
echo -e "\n${YELLOW}4. Verifying structure...${NC}"

# Final structure review
echo "Final directory structure:"
find . -type d -not -path "*/\.*" -not -path "*/venv*" -not -path "*/node_modules*" -not -path "*backup_*" -maxdepth 2 | sort

echo -e "\n${GREEN}Project structure standardized!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Run tests to verify everything works: ./scripts/run_tests.sh"
echo -e "2. Manually check that imports are working properly"
echo -e "3. Once verified, you can safely remove the original NovaSystem directory:"
echo -e "   (ONLY after confirming functionality)"