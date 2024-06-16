# # import os
# # # Load environment variables from .env file
# # from dotenv import load_dotenv
# # load_dotenv()

# # # Get the API keys from environment variables
# # # Set the API keys in the environment
# # os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
# # os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# # from crewai import Agent
# # from crewai_tools import SerperDevTool
# # search_tool = SerperDevTool()

# # # Creating a senior researcher agent with memory and verbose mode
# # researcher = Agent(
# #   role='Senior Researcher',
# #   goal='Uncover groundbreaking technologies in {topic}',
# #   verbose=True,
# #   memory=True,
# #   backstory=(
# #     "Driven by curiosity, you're at the forefront of"
# #     "innovation, eager to explore and share knowledge that could change"
# #     "the world."
# #   ),
# #   tools=[search_tool],
# #   allow_delegation=True
# # )

# # # Creating a writer agent with custom tools and delegation capability
# # writer = Agent(
# #   role='Writer',
# #   goal='Narrate compelling tech stories about {topic}',
# #   verbose=True,
# #   memory=True,
# #   backstory=(
# #     "With a flair for simplifying complex topics, you craft"
# #     "engaging narratives that captivate and educate, bringing new"
# #     "discoveries to light in an accessible manner."
# #   ),
# #   tools=[search_tool],
# #   allow_delegation=False
# # )

# # from crewai import Task

# # # Research task
# # research_task = Task(
# #   description=(
# #     "Identify the next big trend in {topic}."
# #     "Focus on identifying pros and cons and the overall narrative."
# #     "Your final report should clearly articulate the key points"
# #     "its market opportunities, and potential risks."
# #   ),
# #   expected_output='A comprehensive 3 paragraphs long report on the latest AI trends.',
# #   tools=[search_tool],
# #   agent=researcher,
# # )

# # # Writing task with language model configuration
# # write_task = Task(
# #   description=(
# #     "Compose an insightful article on {topic}."
# #     "Focus on the latest trends and how it's impacting the industry."
# #     "This article should be easy to understand, engaging, and positive."
# #   ),
# #   expected_output='A 4 paragraph article on {topic} advancements formatted as markdown.',
# #   tools=[search_tool],
# #   agent=writer,
# #   async_execution=False,
# #   output_file='new-blog-post.md'  # Example of output customization
# # )

# # from crewai import Crew, Process
# # # from dotenv import load_dotenv

# # # Forming the tech-focused crew with enhanced configurations
# # crew = Crew(
# #   agents=[researcher, writer],
# #   tasks=[research_task, write_task],
# #   process=Process.sequential  # Optional: Sequential task execution is default
# # )

# # # Starting the task execution process with enhanced feedback
# # result = crew.kickoff(inputs={'topic': 'AI in healthcare'})
# # print(result)


# import os
# from dotenv import load_dotenv
# load_dotenv()

# os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# # os.environ["POCKETBASE_URL"] = os.getenv("POCKETBASE_URL")
# # os.environ["POCKETBASE_API_KEY"] = os.getenv("POCKETBASE_API_KEY")

# from crewai import Agent
# from crewai_tools import SerperDevTool
# pocketbase_docs_tool = SerperDevTool(url='https://www.npmjs.com/package/pocketbase')

# researcher = Agent(
#     role='PocketBase Researcher',
#     goal='Design a basic CRUD API for a PocketBase database',
#     verbose=True,
#     memory=True,
#     backstory=(
#         "Completely obsessed with PocketBase, you're deeply knowledgeable about its inner workings and are always on the lookout for new ways to leverage its capabilities."
#     ),
#     tools=[pocketbase_docs_tool],
#     allow_delegation=True
# )

# writer = Agent(
#     role='Writer',
#     goal='Document the designed PocketBase CRUD API',
#     verbose=True,
#     memory=True,
#     backstory=(
#         "With a flair for simplifying complex topics, you craft"
#         "engaging narratives that captivate and educate, bringing new"
#         "discoveries to light in an accessible manner."
#     ),
#     tools=[pocketbase_docs_tool],
#     allow_delegation=False
# )

# coder = Agent(
#     role='JavaScript Developer',
#     goal='Implement the designed PocketBase CRUD API',
#     verbose=True,
#     memory=True,
#     backstory=(
#         "With a flair for simplifying complex topics, you craft"               
#         "clean and logically complete code that flows and functions well, right out of the box."
#     ),
#     tools=[pocketbase_docs_tool],
#     allow_delegation=False
# )

# from crewai import Task

# research_task = Task(
#     description=(
#         "Design a basic CRUD API for a PocketBase database."
#         "Focus on creating endpoints for creating, reading, updating, and deleting records."
#         "Your final report should clearly articulate the API endpoints, using the PocketBase API routes from the documentation, request/response formats, and any necessary authentication or authorization."
#     ),
#     expected_output='A comprehensive report on the designed PocketBase CRUD API.',
#     tools=[pocketbase_docs_tool],
#     agent=researcher,
# )

# write_task = Task(
#     description=(
#         "Document the designed PocketBase CRUD API."
#         "Focus on providing clear explanations and examples for each endpoint."
#         "The documentation should be easy to understand and follow for developers."
#     ),
#     expected_output='API documentation for the designed PocketBase CRUD API formatted as markdown.',
#     tools=[pocketbase_docs_tool],
#     agent=writer,
#     async_execution=False,
#     output_file='pocketbase-javascriptsdk-api-docs.md'
# )

# code_task = Task(
#     description=(
#         "Implement the designed PocketBase CRUD API."
#         "Focus on creating endpoints for creating, reading, updating, and deleting records using the PocketBase JavaScript SDK."
#         "Your final report should clearly articulate the API endpoints, using the PocketBase API routes from the documentation, request/response formats, and any necessary authentication or authorization."
#     ),
#     expected_output='JavaScript code to interact with a PocketBase backend.',
#     tools=[pocketbase_docs_tool],
#     agent=researcher,
# )

# from crewai import Crew, Process

# crew = Crew(
#     agents=[researcher, writer, coder],
#     tasks=[research_task, write_task, code_task],
#     process=Process.sequential
# )

# result = crew.kickoff(inputs={'topic': 'PocketBase CRUD API'})
# print(result)



from langchain.llms import Ollama
import os
import logging
from configparser import ConfigParser
from crewai import Agent, Crew, Task, Process
from crewai_tools import BaseTool, DirectoryReadTool, FileReadTool, tool

# Load configuration settings
config = ConfigParser()
config.read('config.ini')
logging_level = config.get('Settings', 'logging_level', fallback='INFO')
default_document_dir = config.get('Settings', 'default_windows_document_dir', fallback='') # Change to match your operating system

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

researcher = Agent(
    role='Researcher',
    goal='Perform in-depth research on the given topic.',
    backstory='An expert in conducting thorough research and analysis.',
    verbose=True,
    allow_delegation=False,
    tools=[directory_read_tool, file_read_tool, document_processor]
)

writer = Agent(
    role='Writer',
    goal='Write a comprehensive report based on the research findings.',
    backstory='An experienced writer with a knack for creating engaging content.',
    verbose=True,
    allow_delegation=False,
)

task1 = Task(description="Perform in-depth research on the given topic.", expected_output="A comprehensive report based on the research findings.", agent=researcher)
task2 = Task(description="Write a comprehensive report based on the research findings.", expected_output="A well-written report based on the research findings.", agent=writer, context=[task1])    


crew = Crew(
    agents=[researcher, writer], 
    tasks=[task1, task2], 
    verbose=2,
    process=Process.sequential
)

result = crew.kickoff(inputs={'topic': 'Devin AI coding assistant.'})

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