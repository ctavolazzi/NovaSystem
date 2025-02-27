"""
Main entry point for the NovaSystem package.

This module is executed when the package is run as a script.
Example: python -m novasystem
"""

import sys
from .cli import main

if __name__ == "__main__":
    # Pass along any command-line arguments
    sys.exit(main())