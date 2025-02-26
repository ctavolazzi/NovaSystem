#!/usr/bin/env python
"""
Direct CLI launcher for NovaSystem.
"""

import os
import sys
import importlib.util

# Add the NovaSystem directory to the Python path
novasystem_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, novasystem_dir)

# Create a mock novasystem package
if "novasystem" not in sys.modules:
    sys.modules["novasystem"] = type('', (), {})()

# Load the necessary modules directly from file paths
modules_to_load = ["nova", "repository", "parser", "docker", "database", "version", "cli"]
base_path = os.path.join(novasystem_dir, "novasystem")

# First load __init__.py
init_path = os.path.join(base_path, "__init__.py")
spec = importlib.util.spec_from_file_location("novasystem.__init__", init_path)
init_module = importlib.util.module_from_spec(spec)
sys.modules["novasystem.__init__"] = init_module
spec.loader.exec_module(init_module)

# Now load each module
for module_name in modules_to_load:
    module_path = os.path.join(base_path, f"{module_name}.py")
    print(f"Loading {module_name} from: {module_path}")

    spec = importlib.util.spec_from_file_location(f"novasystem.{module_name}", module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"novasystem.{module_name}"] = module
    try:
        spec.loader.exec_module(module)
        print(f"Successfully loaded {module_name}")
    except Exception as e:
        print(f"Error loading {module_name}: {e}")

# Get the CLI module
cli_module = sys.modules.get("novasystem.cli")

# Run the main function
if __name__ == "__main__" and cli_module:
    # Add arguments from command line
    args = sys.argv[1:]
    print(f"Running with arguments: {args}")
    try:
        sys.exit(cli_module.main(args))
    except Exception as e:
        print(f"Error running CLI: {e}")
else:
    print("CLI module was not loaded successfully.")