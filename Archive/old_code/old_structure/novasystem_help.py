#!/usr/bin/env python3
"""
Direct runner for NovaSystem CLI help.
"""

import os
import sys

# Determine the project root and add to path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import the CLI module directly from the proper location
from NovaSystem.cli import main

if __name__ == "__main__":
    # Run with --help flag
    sys.exit(main(["--help"]))