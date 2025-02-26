"""
A simple test file to verify imports are working correctly from the root directory.
"""
import sys
import os
from pathlib import Path

# Add NS-bytesize to path
ns_bytesize_path = Path(__file__).parent.parent
if str(ns_bytesize_path) not in sys.path:
    sys.path.insert(0, str(ns_bytesize_path))

import pytest
from utils.autogen_setup import AutogenSetup
from utils.ollama_service import OllamaService, OllamaConfig

def test_imports_working():
    """Test that imports are working correctly."""

    # Test AutogenSetup import
    setup = AutogenSetup(use_ollama=True, model_name="llama3")
    assert setup.model_name == "llama3"

    # Test OllamaService import
    config = OllamaConfig()
    assert config.default_model == "llama3"  # Should be updated to llama3

    print("All imports working correctly!")

if __name__ == "__main__":
    # This can be run directly with python -m examples.simple_test
    test_imports_working()
    print("Test completed successfully!")