"""
This file sets up the test environment for NS-bytesize tests.
It's designed to work when tests are run from:
1. The NS-bytesize directory directly
2. The root NovaSystem directory
"""
import sys
import os
from pathlib import Path

# Get the absolute path to the NS-bytesize directory (parent of tests directory)
ns_bytesize_path = Path(__file__).parent.parent.absolute()

# Add the NS-bytesize directory to Python path if not already there
if str(ns_bytesize_path) not in sys.path:
    sys.path.insert(0, str(ns_bytesize_path))
    print(f"Added {ns_bytesize_path} to Python path")

# Print current working directory and Python path for debugging
print(f"NS-bytesize conftest - Current working directory: {os.getcwd()}")
print(f"NS-bytesize conftest - Python path: {sys.path}")

# Explicitly register this module with a unique name to avoid conflicts
sys.modules['ns_bytesize_conftest'] = sys.modules[__name__]