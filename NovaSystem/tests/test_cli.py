#!/usr/bin/env python3
"""
Test script to verify the CLI functionality.
"""

import os
import sys
import importlib.util

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Testing NovaSystem CLI ===")
try:
    from novasystem.cli import main
    print(f"✅ Successfully imported main function from CLI module")

    # Run the CLI with --help
    print("\nRunning CLI with --help:")
    print("-" * 50)

    # Temporarily set sys.argv to simulate command-line args
    original_argv = sys.argv
    sys.argv = [sys.argv[0], "--help"]

    try:
        exit_code = main()
        print("-" * 50)
        print(f"CLI completed with exit code: {exit_code}")
    except SystemExit as e:
        print("-" * 50)
        print(f"CLI exited with code: {e.code}")
    finally:
        # Restore original argv
        sys.argv = original_argv

except ImportError as e:
    print(f"❌ Import error: {e}")

if __name__ == "__main__":
    print("\nCLI test complete!")