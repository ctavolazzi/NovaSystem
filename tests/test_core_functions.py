#!/usr/bin/env python3
"""
Test Core Functions
------------------
This script tests core functions of the novasystem package without Docker dependencies.
"""

import sys
import os
from pathlib import Path

# Import core modules directly to avoid Docker initialization
from novasystem.repository import RepositoryHandler
from novasystem.parser import DocumentationParser, CommandSource, CommandType

def test_repository_handler():
    """Test basic repository handler functionality."""
    print("\n=== Testing RepositoryHandler ===")

    # Create a simple test repository
    test_repo_path = Path("./test_repo").absolute()
    if not test_repo_path.exists():
        print(f"Creating test repository at {test_repo_path}")
        test_repo_path.mkdir(exist_ok=True)
        with open(test_repo_path / "README.md", "w") as f:
            f.write("# Test Repository\n\nThis is a test repository for NovaSystem.")

    # Initialize repository handler
    print("Initializing RepositoryHandler...")
    repo_handler = RepositoryHandler()

    # Test finding documentation file
    print(f"Testing with local repository: {test_repo_path}")
    doc_file = repo_handler.find_documentation_file(str(test_repo_path))
    print(f"Documentation file found: {doc_file}")

    # Test reading documentation
    if doc_file:
        print("\nReading documentation:")
        doc_content = repo_handler.read_documentation(doc_file)
        print(doc_content)

    # Test finding configuration files
    print("\nFinding configuration files:")
    config_files = repo_handler.find_configuration_files(str(test_repo_path))
    if config_files:
        print("Configuration files found:")
        for file_type, file_path in config_files.items():
            print(f"  {file_type}: {file_path}")
    else:
        print("No configuration files found.")

    print("\nRepository handler test completed successfully.")

def test_documentation_parser():
    """Test basic documentation parser functionality."""
    print("\n=== Testing DocumentationParser ===")

    # Create a test markdown file
    test_md = """
# Test Documentation

## Installation
Install using pip:
```bash
pip install test-package
```

## Usage
```python
import test_package
test_package.hello()
```
    """

    # Initialize parser
    print("Initializing DocumentationParser...")
    parser = DocumentationParser()

    # Test getting installation commands
    print("Extracting installation commands...")
    commands = parser.get_installation_commands(test_md)

    print("\nExtracted Commands:")
    for i, cmd in enumerate(commands):
        print(f"Command {i+1}:")
        print(f"  Text: {cmd.text}")
        print(f"  Type: {cmd.command_type}")
        print(f"  Source: {cmd.source}")
        print(f"  Priority: {cmd.priority}")
        if cmd.context:
            print(f"  Context: {cmd.context[:50]}...")
        print()

    print("Documentation parser test completed successfully.")

def main():
    """Run all tests."""
    print("=== NovaSystem Core Functions Test ===")

    tests = [
        test_repository_handler,
        test_documentation_parser,
    ]

    for test_func in tests:
        try:
            test_func()
            print(f"✅ {test_func.__name__} passed")
        except Exception as e:
            print(f"❌ {test_func.__name__} failed: {str(e)}")
            import traceback
            traceback.print_exc()

    print("\n=== Test Summary ===")
    print("Core function tests completed")

if __name__ == "__main__":
    main()