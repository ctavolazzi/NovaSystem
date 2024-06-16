import os
from dotenv import load_dotenv
load_dotenv()

import os
import logging
from configparser import ConfigParser
from crewai_tools import BaseTool
from crewai import Agent

# Load configuration settings
config = ConfigParser()
config.read('config.ini')
logging_level = config.get('Settings', 'logging_level', fallback='INFO')
default_document_dir = config.get('Settings', 'default_document_dir', fallback='')

# Load environment variables
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentProcessor(BaseTool):
    name: str = "Markdown Document Processor"
    description: str = "Summarizes document contents, identifying key sections and listing them in Markdown format."

    def _run(self, document_content: str) -> str:
        lines = document_content.split('\n')
        summary_lines = [line for line in lines if line.startswith('#')]
        markdown_summary = '\n'.join(summary_lines)
        return markdown_summary

class DocumentInterpreter(BaseTool):
    name: str = "Document Interpreter"
    description: str = "Interprets the processed document summary and provides insights."

    def _run(self, processed_summary: str) -> str:
        insights = f"Key insights from the document:\n{processed_summary}\n\nAdditional analysis needed for each section."
        return insights

class ProjectPlanner(BaseTool):
    name: str = "Project Planner"
    description: str = "Creates a project plan based on the interpreted document summary."

    def _run(self, interpreted_summary: str) -> str:
        plan = f"Project Plan:\n\n{interpreted_summary}\n\nNext steps:\n1. Conduct detailed analysis of each section\n2. Identify dependencies and resources needed\n3. Create timeline and milestones"
        return plan

document_processor = DocumentProcessor()
document_interpreter = DocumentInterpreter()
project_planner = ProjectPlanner()

interpreter_agent = Agent(
    role='Document Analyst',
    goal='Interpret and provide insights on processed document summaries.',
    backstory='An expert in analyzing and deriving insights from document summaries.',
    tools=[document_interpreter]
)

planner_agent = Agent(
    role='Project Planner',
    goal='Create project plans based on interpreted document summaries.',
    backstory='Skilled in translating insights into actionable project plans.',
    tools=[project_planner]
)

def read_document(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        return f"Failed to read document: {e}"

def get_file_path_from_user() -> str:
    """
    Prompts the user for a file path until a valid path is provided or the user cancels the operation.
    """
    while True:
        file_path = input(f"Please enter the file path to your document (default: {default_document_dir}): ").strip()
        if not file_path:
            file_path = default_document_dir
        if os.path.isfile(file_path):
            return file_path
        else:
            logging.error(f"The file at {file_path} does not exist.")
            try_again = input("Would you like to try a new path? (yes/no): ").strip().lower()
            if try_again != 'yes':
                logging.info("Operation cancelled by the user.")
                return None

def process_document(processor: DocumentProcessor, file_path: str) -> str:
    document_content = read_document(file_path)
    if document_content.startswith("Failed to read document:"):
        return document_content
    processed_summary = processor._run(document_content)
    return processed_summary

def interpret_summary(interpreter: Agent, processed_summary: str) -> str:
    interpretation_result = interpreter.tools[0]._run(processed_summary)
    return interpretation_result

def create_project_plan(planner: Agent, interpreted_summary: str) -> str:
    planning_result = planner.tools[0]._run(interpreted_summary)
    return planning_result

def display_summary_info(processed_summary: str, interpreted_summary: str, project_plan: str) -> None:
    """
    Displays the processed summary, interpreted summary, and project plan.
    """
    print(f"Processed Summary:\n{processed_summary}\n")
    print(f"Interpreted Summary:\n{interpreted_summary}\n")
    print(f"Project Plan:\n{project_plan}")

def run_document_workflow() -> None:
    """
    Runs the document processing workflow.
    """
    file_path = get_file_path_from_user()
    if not file_path:
        return
    processed_summary = process_document(document_processor, file_path)
    if processed_summary.startswith("Failed to read document:"):
        logging.error(processed_summary)
        return
    interpreted_summary = interpret_summary(interpreter_agent, processed_summary)
    project_plan = create_project_plan(planner_agent, interpreted_summary)
    display_summary_info(processed_summary, interpreted_summary, project_plan)

def main():
    logging.info("Starting the document processing workflow.")
    run_document_workflow()
    logging.info("Document processing workflow completed.")

if __name__ == "__main__":
    main()