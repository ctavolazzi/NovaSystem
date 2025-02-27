#!/bin/bash
# NovaSystem Standardization from Backup Script

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Standardization from Backup${NC}"
echo "-------------------------------------"

# Create backups directory if it doesn't exist
mkdir -p backups

# Find the latest backup directory
LATEST_BACKUP=$(find ./backups -maxdepth 1 -name "backup_*" -type d | sort | tail -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo -e "${RED}Error: No backup directory found in ./backups!${NC}"
    echo "Creating a new backup before proceeding..."

    # Create a timestamped backup directory
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="./backups/backup_${TIMESTAMP}"
    mkdir -p "$BACKUP_DIR"

    # Copy important files/directories to backup
    echo "Backing up NovaSystem directory..."
    if [ -d "NovaSystem" ]; then
        cp -rf NovaSystem "$BACKUP_DIR/" 2>/dev/null
        echo "NovaSystem directory backed up to $BACKUP_DIR"
    else
        echo "NovaSystem directory not found, skipping backup of this directory."
    fi

    # Set the latest backup to the one we just created
    LATEST_BACKUP="$BACKUP_DIR"
    echo -e "${GREEN}Created new backup at: $LATEST_BACKUP${NC}"
fi

echo -e "\n${YELLOW}Using backup directory: $LATEST_BACKUP${NC}"

# Create the novasystem package directory at the root
echo -e "\n${YELLOW}1. Creating novasystem package at root...${NC}"

# Remove existing directory if it exists
if [ -d "novasystem" ]; then
    echo "Removing existing novasystem directory..."
    rm -rf novasystem
fi

# Create fresh directory
mkdir -p novasystem
echo "Created fresh novasystem directory"

# Copy Python files from backup to novasystem
echo "Copying Python files from backup to novasystem/"
cp -f "$LATEST_BACKUP/NovaSystem"/*.py novasystem/ 2>/dev/null || true
cp -f "$LATEST_BACKUP/NovaSystem/github_docker_integration.md" novasystem/ 2>/dev/null || true

# Verify files were actually copied
echo -e "\n${YELLOW}2. Verifying package structure...${NC}"
ls -la novasystem/
if [ -f "novasystem/__init__.py" ] && [ -f "novasystem/cli.py" ]; then
    echo -e "${GREEN}Package structure created successfully!${NC}"
else
    echo -e "${RED}Failed to create proper package structure!${NC}"

    # Try the capitalized directory as fallback
    echo "Trying files from backup NovaSystem/NovaSystem/"
    cp -f "$LATEST_BACKUP/NovaSystem/NovaSystem"/*.py novasystem/ 2>/dev/null || true

    # Try the lowercase directory as another fallback
    echo "Trying files from backup NovaSystem/novasystem/"
    cp -f "$LATEST_BACKUP/NovaSystem/novasystem"/*.py novasystem/ 2>/dev/null || true

    # Check again
    if [ -f "novasystem/__init__.py" ] && [ -f "novasystem/cli.py" ]; then
        echo -e "${GREEN}Package structure created successfully on second attempt!${NC}"
    else
        echo -e "${RED}Failed to create proper package structure after multiple attempts!${NC}"
        exit 1
    fi
fi

# Create pyproject.toml at the root if not already present
if [ ! -f "pyproject.toml" ]; then
    if [ -f "$LATEST_BACKUP/NovaSystem/pyproject.toml" ]; then
        echo -e "\n${YELLOW}3. Copying pyproject.toml to root...${NC}"
        cp "$LATEST_BACKUP/NovaSystem/pyproject.toml" ./
        echo -e "${GREEN}pyproject.toml copied to root${NC}"
    elif [ -f "$LATEST_BACKUP/pyproject.toml" ]; then
        echo -e "\n${YELLOW}3. Copying pyproject.toml to root...${NC}"
        cp "$LATEST_BACKUP/pyproject.toml" ./
        echo -e "${GREEN}pyproject.toml copied to root${NC}"
    fi
fi

# Force create a tests directory
echo -e "\n${YELLOW}4. Creating tests directory...${NC}"
mkdir -p tests

# Copy tests from backup to tests
if [ -d "$LATEST_BACKUP/NovaSystem/tests" ]; then
    echo "Copying tests from backup NovaSystem/tests/"
    cp -rf "$LATEST_BACKUP/NovaSystem/tests"/* tests/ 2>/dev/null || true
fi

# Also copy our new test_novasystem_pytest.py if it exists
if [ -f "tests/test_novasystem_pytest.py" ]; then
    echo "Found existing pytest-compatible test file"
else
    echo "Creating pytest-compatible test file..."
    cat > tests/test_novasystem_pytest.py << 'EOF'
#!/usr/bin/env python3
"""
Pytest-compatible tests for the novasystem package.
"""

import pytest

class TestNovaSystemImports:
    """Test basic imports from the novasystem package."""

    def test_package_import(self):
        """Test importing the novasystem package."""
        import novasystem
        assert hasattr(novasystem, '__version__')
        assert hasattr(novasystem, '__file__')

    def test_core_modules_import(self):
        """Test importing core modules from novasystem."""
        from novasystem import cli, repository, parser, docker, database
        assert hasattr(cli, 'main')
        assert hasattr(repository, 'RepositoryHandler')
        assert hasattr(parser, 'DocumentationParser')
        assert hasattr(docker, 'DockerExecutor')
        assert hasattr(database, 'DatabaseManager')

    def test_core_classes_import(self):
        """Test importing core classes from novasystem."""
        import novasystem
        assert hasattr(novasystem, 'RepositoryHandler')
        assert hasattr(novasystem, 'DocumentationParser')
        assert hasattr(novasystem, 'DockerExecutor')
        assert hasattr(novasystem, 'DatabaseManager')

if __name__ == "__main__":
    # This file can also be run directly
    pytest.main(["-v", __file__])
EOF
    echo -e "${GREEN}Created pytest-compatible test file${NC}"
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
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Run the sanity check: python scripts/test_sanity_check.py"
echo -e "2. Run the tests: ./scripts/run_tests.sh"