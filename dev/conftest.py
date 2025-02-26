import sys
import os
from pathlib import Path

# Root directory of the project
root_path = Path(__file__).parent.absolute()

# Add paths to sys.path to make imports work from root
paths_to_add = [
    # Main project paths
    str(root_path),

    # NS-bytesize paths
    str(root_path / "dev" / "NS-bytesize"),
    str(root_path / "dev" / "NS-bytesize" / "utils"),
    str(root_path / "dev" / "NS-bytesize" / "tests"),
    str(root_path / "dev" / "NS-bytesize" / "hubs"),
    str(root_path / "dev" / "NS-bytesize" / "bots"),

    # NovaSystem paths
    str(root_path / "NovaSystem"),
    str(root_path / "NovaSystem" / "backend"),
    str(root_path / "NovaSystem" / "core"),
]

# Add all paths to sys.path if not already there
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# Create mock for colorama if needed (as mentioned in your devlog)
try:
    import colorama
except ImportError:
    import types

    # Create a mock colorama module
    colorama_mock = types.ModuleType("colorama")

    # Mock the init function
    def mock_init(*args, **kwargs):
        return

    # Mock Fore, Back, Style classes
    class MockColors:
        RED = ""
        GREEN = ""
        YELLOW = ""
        BLUE = ""
        MAGENTA = ""
        CYAN = ""
        WHITE = ""
        BLACK = ""
        RESET = ""

    colorama_mock.init = mock_init
    colorama_mock.Fore = MockColors()
    colorama_mock.Back = MockColors()
    colorama_mock.Style = MockColors()

    # Add the mock to sys.modules
    sys.modules["colorama"] = colorama_mock
    print("Created mock colorama module")

print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")