import os
import logging
from configparser import ConfigParser
from crewai import Agent, Crew, Task
from crewai_tools import BaseTool, DirectoryReadTool, FileReadTool, tool

# Load configuration settings
config = ConfigParser()
config.read('config.ini')
logging_level = config.get('Settings', 'logging_level', fallback='INFO')
default_document_dir = config.get('Settings', 'default_document_dir', fallback='')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging_level, format='%(asctime)s - %(levelname)s - %(message)s')

# Instantiate tools
directory_read_tool = DirectoryReadTool()
file_read_tool = FileReadTool()

@tool("Plain Text Document Processor")
def document_processor(document_content: str) -> str:
    """Processes plain text document contents."""
    return document_content.strip()

# Instantiate agents
insights_extractor = Agent(
    role='Insights Extractor',
    goal='Extract key insights from the processed document content.',
    backstory='An expert in identifying and summarizing key points from plain text documents.',
    max_iter=3,
    verbose=True,
    tools=[document_processor]
)

document_interpreter = Agent(
    role='Document Interpreter',
    goal='Interpret the key insights from the document and provide a detailed analysis.',
    backstory='An expert in analyzing and providing detailed interpretations of document insights.',
    max_iter=3,
    verbose=True,
    tools=[file_read_tool]
)

project_planner = Agent(
    role='Project Planner',
    goal='Create a comprehensive project plan based on the document interpretation.',
    backstory='Skilled in translating insights into actionable project plans.',
    max_iter=3,
    verbose=True,
    tools=[directory_read_tool]
)

def read_document(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        logging.error(f"Failed to read document: {e}")
        return None

def get_file_path_from_user() -> str:
    file_path = input(f"Please enter the file path to your document (default: {default_document_dir}): ").strip()
    if not file_path:
        file_path = default_document_dir
    if os.path.isfile(file_path):
        return file_path
    else:
        logging.error(f"The file at {file_path} does not exist.")
        return None
def run_document_workflow(file_path: str):
    document_content = read_document(file_path)
    if document_content is None:
        logging.error("No document content to process.")
        return

    extract_insights_task = Task(
        description="Extract key insights from the processed document content.",
        expected_output="A list of key insights from the document.",
        agent=insights_extractor,
        input=document_content
    )

    interpret_insights_task = Task(
        description="Interpret the key insights from the document and provide a detailed analysis.",
        expected_output="A detailed interpretation and analysis of the key insights.",
        agent=document_interpreter,
        context=[extract_insights_task]
    )

    plan_project_task = Task(
        description="Create a comprehensive project plan based on the document interpretation.",
        expected_output="A detailed project plan based on the interpreted insights.",
        agent=project_planner,
        context=[interpret_insights_task]
    )

    crew = Crew(
        agents=[insights_extractor, document_interpreter, project_planner],
        tasks=[extract_insights_task, interpret_insights_task, plan_project_task]
    )

    result = crew.kickoff()

    logging.info(f"Extracted Insights:\n{extract_insights_task.output.raw_output}")
    logging.info(f"Interpreted Insights:\n{interpret_insights_task.output.raw_output}")
    logging.info(f"Project Plan:\n{plan_project_task.output.raw_output}")

def get_file_path_from_user() -> str:
    file_path = input(f"Please enter the file path to your document (default: {default_document_dir}): ").strip()
    if not file_path:
        file_path = default_document_dir
    elif not os.path.isabs(file_path):
        file_path = os.path.join(default_document_dir, file_path)
    if os.path.isfile(file_path):
        return file_path
    else:
        logging.error(f"The file at {file_path} does not exist.")
        return None

def main():
    logging.info("Starting the document processing workflow.")
    file_path = get_file_path_from_user()
    if file_path:
        run_document_workflow(file_path)
    else:
        logging.info("Operation cancelled by the user.")

if __name__ == "__main__":
    main()