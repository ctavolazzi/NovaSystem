#!/usr/bin/env python3
"""
Direct runner for NovaSystem CLI.
This script bypasses the packaging system and directly imports the CLI.
"""

import sys
import os

# Add the current directory to the path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from NovaSystem.cli import main
    sys.exit(main())
except ImportError as e:
    print(f"Error importing NovaSystem CLI: {e}")
    print("\nDEBUG INFO:")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Python executable: {sys.executable}")
    sys.exit(1)