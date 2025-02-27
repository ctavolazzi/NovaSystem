#!/usr/bin/env python3
"""
Test Sanity Check Script
------------------------
This script performs basic sanity checks before running tests to identify common issues.
Run this before your test suite to ensure the environment is properly set up.

Usage:
    python scripts/test_sanity_check.py
"""

import importlib
import os
import sys
import subprocess
from pathlib import Path

def check_imports():
    """Verify that critical modules can be imported."""
    critical_modules = [
        "pytest",
        "novasystem",
        "requests",
        "docker",
        "tqdm",
        "gitpython"
    ]

    success = True
    for module in critical_modules:
        try:
            # Special case for gitpython which is imported as 'git'
            if module == "gitpython":
                module_to_import = "git"
            else:
                module_to_import = module

            importlib.import_module(module_to_import)
            print(f"✅ Successfully imported {module}")
        except ImportError as e:
            print(f"❌ Failed to import {module}: {e}")
            success = False

    return success

def check_paths():
    """Verify critical paths exist in the project."""
    # Determine project root (parent directory of this script)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # In the standardized structure, these paths should exist
    critical_paths = [
        project_root / "tests",        # Tests directory at root
        project_root / "novasystem",   # Package at root
        project_root / "pyproject.toml" # Config at root
    ]

    success = True
    for path in critical_paths:
        if path.exists():
            print(f"✅ Path exists: {path}")
        else:
            print(f"❌ Missing path: {path}")
            if path.name == "pyproject.toml":
                print("   pyproject.toml should be at the project root in a standardized structure")
            elif path.name == "tests":
                print("   Tests should be in a 'tests' directory at the project root")
            elif path.name == "novasystem":
                print("   Package code should be in a 'novasystem' directory at the project root")

            if not (project_root / "scripts" / "standardize_project.sh").exists():
                print("   You may need to standardize your project structure")
            else:
                print("   Run ./scripts/standardize_project.sh to fix your project structure")

            success = False

    return success

def check_pytest_collection():
    """Run pytest in collection-only mode to check for test discovery issues."""
    print("\nChecking test discovery...")
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            num_tests = result.stdout.strip().split(" ")[0]
            print(f"✅ Found {num_tests} tests")
            return True
        else:
            print(f"❌ Test collection failed:\n{result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Failed to run pytest: {e}")
        return False

def main():
    """Run all sanity checks."""
    print("=== NovaSystem Test Sanity Check ===\n")

    checks = [
        ("Import check", check_imports),
        ("Path check", check_paths),
        ("Test discovery check", check_pytest_collection)
    ]

    all_passed = True
    for name, check_func in checks:
        print(f"\n--- {name} ---")
        if not check_func():
            all_passed = False

    print("\n=== Summary ===")
    if all_passed:
        print("✅ All sanity checks passed - you're good to go!")
        return 0
    else:
        print("❌ Some checks failed - please fix the issues before running tests")
        return 1

if __name__ == "__main__":
    sys.exit(main())