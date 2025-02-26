import sys
import os
from pathlib import Path

# Get the absolute path to the NS-bytesize directory (parent of examples directory)
ns_bytesize_path = Path(__file__).parent.parent.absolute()

# Add the NS-bytesize directory to Python path if not already there
if str(ns_bytesize_path) not in sys.path:
    sys.path.insert(0, str(ns_bytesize_path))
    print(f"Added {ns_bytesize_path} to Python path")

# Print current working directory and Python path for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")