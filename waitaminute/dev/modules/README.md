# Document Processing Workflow

This script processes a document, interprets its summary, and creates a project plan using the CrewAI framework.

## Prerequisites

- Python 3.x
- CrewAI library
- CrewAI Tools library

## Configuration

The script can be configured using the `config.ini` file:

- `logging_level`: The logging level for the script (e.g., INFO, DEBUG, WARNING, ERROR).
- `default_document_dir`: The default directory to search for documents.

## Usage

1. Install the required libraries:
pip install crewai crewai-tools


Copy code

2. Run the script:
python document_processor.py


Copy code

3. Follow the prompts to enter the file path of the document you want to process.

4. The script will display the processed summary, interpreted summary, and project plan.

## Functions

- `get_file_path_from_user()`: Prompts the user for a file path until a valid path is provided or the user cancels the operation.
- `read_document(file_path: str) -> str`: Reads the contents of a document from the given file path.
- `process_document(processor: DocumentProcessor, file_path: str) -> str`: Processes the document using the provided DocumentProcessor.
- `interpret_summary(interpreter: Agent, processed_summary: str) -> str`: Interprets the processed summary using the provided interpreter agent.
- `create_project_plan(planner: Agent, interpreted_summary: str) -> str`: Creates a project plan based on the interpreted summary using the provided planner agent.
- `display_summary_info(processed_summary: str, interpreted_summary: str, project_plan: str) -> None`: Displays the processed summary, interpreted summary, and project plan.
- `run_document_workflow() -> None`: Runs the document processing workflow.
- `main()`: The main function that orchestrates the document processing workflow.