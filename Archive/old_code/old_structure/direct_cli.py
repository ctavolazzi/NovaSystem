#!/usr/bin/env python
"""
Direct CLI runner for NovaSystem.

This script directly runs the CLI functionality without relying on the package installation.
Usage: python direct_cli.py [arguments]
Example: python direct_cli.py --help
"""

import os
import sys

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
novasystem_dir = os.path.join(current_dir, "novasystem")

# Directly import what we need from the module files
sys.path.insert(0, current_dir)

# Run the main CLI function
if __name__ == "__main__":
    try:
        # Execute the cli.py file directly as a script
        cli_path = os.path.join(novasystem_dir, "cli.py")
        with open(cli_path) as f:
            cli_code = compile(f.read(), cli_path, 'exec')

        # Set up globals for the script
        script_globals = {
            '__file__': cli_path,
            '__name__': '__main__',
            '__package__': 'novasystem',
            'sys': sys
        }

        # Pass command-line arguments
        if len(sys.argv) > 1:
            # Remove this script's name and keep the rest of the arguments
            sys.argv = sys.argv[1:]

        # Run the CLI script
        print(f"Running NovaSystem CLI directly with arguments: {sys.argv}")
        exec(cli_code, script_globals)

    except Exception as e:
        print(f"Error running CLI: {e}")
        sys.exit(1)