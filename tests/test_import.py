#!/usr/bin/env python3
"""
Test script to verify imports from the novasystem package.
"""

import os
import sys
import importlib

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Testing NovaSystem Imports ===")
try:
    import novasystem
    print(f"✅ Successfully imported novasystem package")
    print(f"   Version: {novasystem.__version__}")
    print(f"   Package location: {novasystem.__file__}")

    # Try to import the CLI module
    from novasystem import cli
    print(f"✅ Successfully imported novasystem.cli")
    print(f"   Has main function: {hasattr(cli, 'main')}")

    # Try to import other key modules
    from novasystem import repository, parser, docker, database
    print(f"✅ Successfully imported all core modules")

    # Check if imported classes are available
    print("\nImported classes:")
    print(f"✅ RepositoryHandler: {novasystem.RepositoryHandler.__name__}")
    print(f"✅ DocumentationParser: {novasystem.DocumentationParser.__name__}")
    print(f"✅ DockerExecutor: {novasystem.DockerExecutor.__name__}")
    print(f"✅ DatabaseManager: {novasystem.DatabaseManager.__name__}")

except ImportError as e:
    print(f"❌ Import error: {e}")

    # Print sys.path for debugging
    print("\nPython path:")
    for i, path in enumerate(sys.path):
        print(f"  {i}. {path}")

    print("\nChecking for novasystem directory:")
    for path in sys.path:
        potential_module = os.path.join(path, "novasystem")
        if os.path.isdir(potential_module):
            print(f"  Found at: {potential_module}")
            print(f"  Contains __init__.py: {os.path.isfile(os.path.join(potential_module, '__init__.py'))}")
            print(f"  Files: {os.listdir(potential_module)}")

if __name__ == "__main__":
    print("\nTest complete!")