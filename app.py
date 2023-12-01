import os
import json
from pathlib import Path
import time
import glob

# Constants
APP_NAME = "NovaSystem"
NOVASYSTEM_WORKSPACE = f"{APP_NAME}_Workspace_{time.time_ns()}"
REQUIRED_SETUP_JSON = 'novasystem_required_setup_files.json'

def find_existing_workspaces():
    """ Find existing workspace folders in the current directory. """
    return glob.glob(f"{APP_NAME}_Workspace_*")

def get_user_workspace_choice(existing_workspaces):
    """ Get user's choice for the workspace. """
    print("Existing workspaces found:")
    for i, workspace in enumerate(existing_workspaces, start=1):
        print(f"{i}. {workspace}")

    print("\nOptions:")
    print("1. Use the most recent workspace.")
    print("2. Enter the path to a specific workspace.")
    print("3. Create a new workspace.")
    choice = input("Enter your choice (1/2/3): ").strip()

    return choice

def handle_workspace_choice(choice, existing_workspaces):
    """ Handle the user's workspace choice. """
    if choice == "1" and existing_workspaces:
        # Use the most recent workspace
        return max(existing_workspaces, key=os.path.getctime)
    elif choice == "2":
        # Let the user enter a specific path
        return input("Enter the path to the workspace: ").strip()
    elif choice == "3" or not existing_workspaces:
        # Create a new workspace
        return f"{APP_NAME}_Workspace_{time.time_ns()}"
    else:
        print("Invalid choice. A new workspace will be created.")
        return f"{APP_NAME}_Workspace_{time.time_ns()}"


def load_required_structure():
    """ Load required structure from JSON file. """
    with open(REQUIRED_SETUP_JSON, 'r') as file:
        return json.load(file)

def create_directory(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def create_file(path):
    if not Path(path).exists():
        Path(path).touch()

def setup_environment(structure):
    """ Set up the required directories and files in NovaSystem Workspace """
    base_path = Path(NOVASYSTEM_WORKSPACE)
    for directory in structure['directories']:
        create_directory(base_path / directory)

    for file in structure['files']:
        create_file(base_path / file)

    print(f"Environment setup complete in {base_path.resolve()}.")

def user_interaction():
    """ Simple user interaction: ask for input and echo back. """
    user_input = input("Enter something: ")
    print(f"You entered: {user_input}")

def main_application():
    """ Main application logic after setup """
    print(f"Starting main application in {Path(NOVASYSTEM_WORKSPACE).resolve()}...")
    # Placeholder for main application logic
    print("NovaSystem main application logic goes here.")
    user_interaction()  # Simple user interaction

def run_test():
    """ Simple test to ensure basic functionality. """
    print("Running basic functionality test...")
    # Example test: Check if a specific file exists
    test_file = Path(NOVASYSTEM_WORKSPACE) / "README.md"
    if test_file.exists():
        print("Test passed: README.md exists.")
        return True
    else:
        print("Test failed: README.md does not exist.")
        return False

def verify_installation(base_path, structure):
    """ Verify that all required directories and files exist. """
    missing_items = []
    for directory in structure['directories']:
        if not (base_path / directory).exists():
            missing_items.append(str(base_path / directory))

    for file in structure['files']:
        if not (base_path / file).exists():
            missing_items.append(str(base_path / file))

    # return False # Debugging; intentionally fails verification

    if missing_items:
        print("Missing items in installation:")
        for item in missing_items:
            print(f"- {item}")
        return False
    return True

def main():
    existing_workspaces = find_existing_workspaces()
    workspace_choice = get_user_workspace_choice(existing_workspaces) if existing_workspaces else "3"
    workspace_path = handle_workspace_choice(workspace_choice, existing_workspaces)

    print(f"Using workspace: {workspace_path}")
    required_structure = load_required_structure()
    global NOVASYSTEM_WORKSPACE
    NOVASYSTEM_WORKSPACE = workspace_path
    setup_environment(required_structure)

    base_path = Path(NOVASYSTEM_WORKSPACE)

    if not verify_installation(base_path, required_structure):
        print("Installation verification failed. Please check the logs.")
        return

    if not run_test():
        print("Run test failed. Please check the system's functionality.")
        return

    main_application()  # Start the main application logic

def main_application():
    print(f"Starting main application in {Path(NOVASYSTEM_WORKSPACE).resolve()}...")
    user_interaction()  # Simple user interaction

if __name__ == '__main__':
    main()
