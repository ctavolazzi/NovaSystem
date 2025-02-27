#!/bin/bash
# NovaSystem Project Standardization Script

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Project Standardization${NC}"
echo "--------------------------------"

# Create backup first
echo -e "\n${YELLOW}1. Creating backup...${NC}"
cd "$(dirname "$0")/.."
ROOT_DIR=$(pwd)
BACKUP_DIR="${ROOT_DIR}/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
echo "Creating backup at ${BACKUP_DIR}..."
find . -maxdepth 1 -not -path "./.*" -not -path "./venv" -not -path "./node_modules" -not -path "." -not -path "${BACKUP_DIR}" | xargs -I{} cp -r {} ${BACKUP_DIR}/
echo -e "${GREEN}Backup created at $BACKUP_DIR${NC}"

# Standardize package structure
echo -e "\n${YELLOW}2. Standardizing package structure...${NC}"

# Create standard directory structure if not exist
mkdir -p novasystem
mkdir -p tests

# Move package code from nested location to standard location
if [ -d "NovaSystem/novasystem" ]; then
    echo "Moving package code..."
    # Ensure we preserve files during copying
    cp -rn NovaSystem/novasystem/* novasystem/

    # Check if we need to merge with existing package
    if [ -d "novasystem" ] && [ "$(ls -A novasystem)" ]; then
        echo "Merging with existing package code..."
    fi
    echo -e "${GREEN}Package code moved to standard location${NC}"
fi

# Move tests to standard location
if [ -d "NovaSystem/tests" ]; then
    echo "Moving tests..."
    cp -rn NovaSystem/tests/* tests/
    echo -e "${GREEN}Tests moved to standard location${NC}"
fi

# Check for root tests and merge them if they exist
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo "Merged with existing tests at root level."
fi

# Copy pyproject.toml to root if needed
if [ ! -f "pyproject.toml" ] && [ -f "NovaSystem/pyproject.toml" ]; then
    echo "Moving pyproject.toml..."
    cp NovaSystem/pyproject.toml ./
    echo -e "${GREEN}pyproject.toml moved to root${NC}"
fi

# Update import paths in test files
echo -e "\n${YELLOW}3. Updating import paths in tests...${NC}"
find tests -name "*.py" -type f | xargs sed -i '' 's/from NovaSystem.novasystem/from novasystem/g' || true
find tests -name "*.py" -type f | xargs sed -i '' 's/import NovaSystem.novasystem/import novasystem/g' || true

# Verify and update paths
echo -e "\n${YELLOW}4. Verifying structure...${NC}"

# Final structure review
echo "Final directory structure:"
find . -type d -not -path "*/\.*" -not -path "*/venv*" -not -path "*/node_modules*" -not -path "*backup_*" -maxdepth 2 | sort

echo -e "\n${GREEN}Project structure standardized!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Run tests to verify everything works: ./scripts/run_tests.sh"
echo -e "2. Manually check that imports are working properly"
echo -e "3. Once verified, you can remove redundant directories:"
echo -e "   rm -rf NovaSystem/novasystem NovaSystem/tests (ONLY after confirming functionality)"