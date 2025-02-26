"""
Main entry point for the NovaSystem package.

This module is executed when the package is run as a script.
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())