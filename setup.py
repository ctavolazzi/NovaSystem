import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PROJECT_STRUCTURE_JSON = 'required_structure.json'
ROOT_DIRECTORY = 'NovaSystem'

def load_project_structure():
    try:
        with open(PROJECT_STRUCTURE_JSON, 'r') as file:
            return json.load(file)
    except Exception as e:
        logging.error(f"Error loading project structure: {e}")
        return None

def create_file(file_path):
    path = Path(ROOT_DIRECTORY) / file_path
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        logging.info(f"Created file: {path}")

def setup_project(structure):
    for directory in structure.get("directories", []):
        full_path = Path(ROOT_DIRECTORY) / directory
        full_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {full_path}")
    for file in structure.get("files", []):
        create_file(file)

def main():
    # Create the root directory if it doesn't exist
    Path(ROOT_DIRECTORY).mkdir(exist_ok=True)
    logging.info(f"Created or verified root directory: {ROOT_DIRECTORY}")

    structure = load_project_structure()
    if structure is None:
        logging.error("No project structure loaded. Exiting setup.")
        return

    setup_project(structure)
    logging.info("Project setup completed successfully.")

def setup_novasystem():
    main()

if __name__ == '__main__':
    main()
