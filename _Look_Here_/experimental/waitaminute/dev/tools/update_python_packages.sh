#!/bin/bash

echo "Fetching list of outdated packages..."

# Fetch outdated packages and store them in a variable
outdated_packages=$(pip list --outdated --format=columns | awk 'NR>2 {print $1}')

# Check for errors in fetching outdated packages
if [[ $? -ne 0 ]]; then
  echo "An error occurred while fetching the outdated packages."
  exit 1
fi

# Backup current environment
pip freeze > backup_requirements.txt

# Check if there are any outdated packages
if [[ -z "$outdated_packages" ]]; then
  echo "All packages are up-to-date."
else
  echo "Updating packages..."
  for package in $outdated_packages; do
    pip install --upgrade "$package"
    # Check for dependency conflicts
    conflict=$(pip check 2>&1)
    if [[ ! -z "$conflict" ]]; then
      echo "Dependency conflict detected for package $package. Rolling back..."
      pip install -r backup_requirements.txt
      break
    fi
  done
fi

echo "Running safety check..."
safety check

# Check for errors in safety check
if [[ $? -ne 0 ]]; then
  echo "An error occurred while performing the safety check."
  exit 1
fi

echo "Package update and safety checks are complete."
