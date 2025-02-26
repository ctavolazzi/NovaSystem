import sys
import os
from pathlib import Path

# Get the absolute path to the ai-rpg-test directory (parent of tests directory)
ai_rpg_test_path = Path(__file__).parent.parent.absolute()

# Add the ai-rpg-test directory to Python path if not already there
if str(ai_rpg_test_path) not in sys.path:
    sys.path.insert(0, str(ai_rpg_test_path))
    print(f"Added {ai_rpg_test_path} to Python path")

# Mock colorama module if it's not installed
try:
    import colorama
except ImportError:
    # Create a mock colorama module
    import types
    colorama_mock = types.ModuleType('colorama')

    # Create Fore, Back, and Style classes with color attributes
    class Fore:
        BLACK = ''
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''

    class Back:
        BLACK = ''
        RED = ''
        GREEN = ''
        YELLOW = ''
        BLUE = ''
        MAGENTA = ''
        CYAN = ''
        WHITE = ''
        RESET = ''

    class Style:
        DIM = ''
        NORMAL = ''
        BRIGHT = ''
        RESET_ALL = ''

    # Add classes to the mock module
    colorama_mock.Fore = Fore
    colorama_mock.Back = Back
    colorama_mock.Style = Style
    colorama_mock.init = lambda: None

    # Add the mock to sys.modules
    sys.modules['colorama'] = colorama_mock
    print("Created mock colorama module")

# Print current working directory and Python path for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")