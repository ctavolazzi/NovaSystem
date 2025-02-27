#!/bin/bash
# NovaSystem Backup Creation Script

# Define colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}NovaSystem Backup Creation${NC}"
echo "-------------------------------------"

# Create backups directory if it doesn't exist
mkdir -p backups

# Create a timestamped backup directory
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/backup_${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

echo -e "\n${YELLOW}Creating backup at: $BACKUP_DIR${NC}"

# Backup NovaSystem directory (if it exists)
if [ -d "NovaSystem" ]; then
    echo "Backing up NovaSystem directory..."
    cp -rf NovaSystem "$BACKUP_DIR/" 2>/dev/null
    echo -e "${GREEN}NovaSystem directory backed up to $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}NovaSystem directory not found, skipping.${NC}"
fi

# Backup novasystem directory (if it exists)
if [ -d "novasystem" ]; then
    echo "Backing up novasystem directory..."
    cp -rf novasystem "$BACKUP_DIR/" 2>/dev/null
    echo -e "${GREEN}novasystem directory backed up to $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}novasystem directory not found, skipping.${NC}"
fi

# Backup tests directory (if it exists)
if [ -d "tests" ]; then
    echo "Backing up tests directory..."
    cp -rf tests "$BACKUP_DIR/" 2>/dev/null
    echo -e "${GREEN}tests directory backed up to $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}tests directory not found, skipping.${NC}"
fi

# Backup pyproject.toml (if it exists)
if [ -f "pyproject.toml" ]; then
    echo "Backing up pyproject.toml..."
    cp pyproject.toml "$BACKUP_DIR/" 2>/dev/null
    echo -e "${GREEN}pyproject.toml backed up to $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}pyproject.toml not found, skipping.${NC}"
fi

# Backup scripts directory (if it exists)
if [ -d "scripts" ]; then
    echo "Backing up scripts directory..."
    cp -rf scripts "$BACKUP_DIR/" 2>/dev/null
    echo -e "${GREEN}scripts directory backed up to $BACKUP_DIR${NC}"
else
    echo -e "${YELLOW}scripts directory not found, skipping.${NC}"
fi

echo -e "\n${GREEN}Backup complete!${NC}"
echo -e "Backup created at: $BACKUP_DIR"
echo -e "To restore from this backup, use: ./scripts/standardize_from_backup.sh"