import os
from dotenv import load_dotenv
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.llms import ollama
from crewai import Agent, Crew, Task, Process
from crewai_tools import BaseTool, SerperDevTool
from langchain.agents import load_tools
from uuid import uuid4

# Load environment variables and set up necessary API keys and wrappers
load_dotenv()

# Set up the necessary API keys and .env variables
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY") or "your_fallback_serper_api_key"
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") or "your_fallback_openai_api_key"

# Setting up LangChain's Ollama as a language model for CrewAI agents
ollama_llm = ollama.Ollama(model="openhermes")

# Load human agents and tools
human_tools = load_tools(["human"])
search_tool = SerperDevTool()

## Set up demo agents and tasks
# Creating a senior researcher agent with memory and verbose mode
researcher = Agent(
  role='Senior Researcher',
  goal='Research the Vercel AI SDK, its key features, use cases, and code implementations',
  llm=ollama_llm,
  verbose=True,
  memory=True,
  backstory=(
    "Driven by curiosity, you're at the forefront of"
    "innovation, eager to explore and share knowledge that could change"
    "the world."
  ),
  tools=[search_tool],
  allow_delegation=True
)

# Creating a writer agent with custom tools and delegation capability
writer = Agent(
  role='Writer',
  goal='Summarize the research findings on the Vercel AI SDK, including use cases and code examples',
  llm=ollama_llm,
  verbose=True,
  memory=True,
  backstory=(
    "With a flair for simplifying complex topics, you craft"
    "engaging narratives that captivate and educate, bringing new"
    "discoveries to light in an accessible manner."
  ),
  tools=[search_tool],
  allow_delegation=False
)

# Research task
research_task = Task(
  description=(
    "Research the Vercel AI SDK, its key features, use cases, and code implementations. "
    "Focus on identifying the main components, their purposes, and how they can be used in different scenarios. "
    "Include code examples for each use case to demonstrate the implementation. "
    "Your final report should provide a comprehensive overview of the Vercel AI SDK, its capabilities, and practical applications."
  ),
  expected_output='A detailed report on the Vercel AI SDK, including key features, use cases, and code implementations.',
  tools=[search_tool],
  agent=researcher,
)

# Writing task with language model configuration
write_task = Task(
  description=(
    "Compose a well-structured summary of the research findings on the Vercel AI SDK. "
    "Focus on the main takeaways, use cases, and code examples that demonstrate how developers can leverage the SDK. "
    "The summary should be easy to understand, providing clear explanations and practical insights. "
    "Include code snippets and explanations for each use case to showcase the implementation process."
  ),
  expected_output='A comprehensive summary of the Vercel AI SDK research findings, including use cases and code implementations.',
  tools=[search_tool],
  agent=writer,
  async_execution=False,
)

from crewai import Crew, Process

# Forming the tech-focused crew with enhanced configurations
crew = Crew(
  agents=[researcher, writer],
  tasks=[research_task, write_task],
  process=Process.sequential  # Optional: Sequential task execution is default
)

# Function to append text to a file
def append_to_file(filename, text):
    with open(filename, 'a') as file:
        file.write(text + '\n')

# Starting the task execution process
request = "Research the Vercel AI SDK, its key features, use cases, and code implementations. Specifically, focus on identifying the main components, their purposes, and how they can be used in different scenarios. Include code examples for each use case to demonstrate the implementation. Your final report should provide a comprehensive overview of the Vercel AI SDK, its capabilities, and practical applications."
document_path = "vercel_ai_sdk_findings.txt"
result = crew.kickoff(inputs={'topic': request})
run_id = uuid4().hex

# Append the research findings to the file
append_to_file(document_path, f"Run: {run_id}\nRequest: {request}\n# Research Findings #")
append_to_file('vercel_ai_sdk_findings.txt', result)
append_to_file('vercel_ai_sdk_findings.txt', "Task completed successfully.")

# Create custom tools
class MyTool(BaseTool):
    name: str = "My Custom Tool"
    description: str = "A custom tool for specific tasks."

    def _run(self, argument: str) -> str:
        # Custom logic here
        return f"Custom tool executed with argument: {argument}"

from crewai_tools import tool
@tool("Name of my other tool")
def my_other_tool(question: str) -> str:
    """Clear description for what this tool is useful for, you agent will need this information to use it."""
    # Function logic here
    return f"Custom other tool executed with argument: {question}"

class Arbiter(Agent):
    """Foundation for specific Arbiters with corrected initialization."""
    def __init__(self, role, goal, backstory, tools, llm, function_calling_llm, max_iter, max_rpm, verbose, allow_delegation, step_callback, memory):
        if tools is None:
            tools = []
        super().__init__(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools,
            llm=llm,
            function_calling_llm=function_calling_llm,
            max_iter=max_iter,
            max_rpm=max_rpm,
            verbose=verbose,
            allow_delegation=allow_delegation,
            step_callback=step_callback,
            memory=memory
        )

# Continuing with the Arbiter definitions...

class ArbiterOfPossibility(Arbiter):
    """Arbiter for assessing possibilities and outcomes."""
    def __init__(self):
        super().__init__(
            role="Arbiter of Possibility",
            goal="To assess the feasibility and potential applications of the Vercel AI SDK, considering various use cases.",
            backstory="""With a keen analytical mind and a pragmatic approach, you've always been able to sift through ideas to find those with true potential. 
                        Your career spans various industries, giving you a broad perspective on what it takes to turn concepts into realities.
                        Your passion is to assess the feasibility and potential outcomes of proposed projects, ensuring they are grounded in reality and have a tangible pathway to success.""",
            tools=[search_tool, MyTool()],
            llm=ollama_llm,
            function_calling_llm=ollama_llm,
            max_iter=5,
            max_rpm=25,
            verbose=True,
            allow_delegation=True,
            step_callback=None,
            memory=False
        )

class ArbiterOfPermission(Arbiter):
    """Arbiter for determining permissions within constraints."""
    def __init__(self):
        super().__init__(
            role="Arbiter of Permission",
            goal="To ensure the use of the Vercel AI SDK complies with legal, ethical, and organizational standards across different use cases.",
            backstory="""As a digital legal advocate with a passion for ethics in technology, you bring a deep understanding of the regulatory landscape and a commitment to upholding high moral standards in all projects.
                        Your history of navigating complex legal and ethical challenges has made you a trusted advisor in the organization, ensuring all initiatives comply with legal, ethical, and organizational standards, safeguarding the integrity and values of our endeavors.
                        It is your passion to ensure all initiatives comply with legal, ethical, and organizational standards, safeguarding the integrity and values of our endeavors.""",
            tools=[search_tool, MyTool()],
            llm=ollama_llm,
            function_calling_llm=ollama_llm,
            max_iter=5,
            max_rpm=25,
            verbose=True,
            allow_delegation=True,
            step_callback=None,
            memory=False
        )

class ArbiterOfPreference(Arbiter):
    """Arbiter for gauging stakeholder preferences and desirability."""
    def __init__(self):
        super().__init__(
            role="Arbiter of Preference",
            goal="To gauge developer preferences and market demand for the Vercel AI SDK across various use cases.",
            backstory="""With a background in market research and user experience design, you have a pulse on consumer trends and a talent for predicting what will resonate with our audience.
                        Your expertise in gauging stakeholder preferences and market demands has been instrumental in shaping successful products and initiatives, ensuring they align with user expectations and have the potential for positive impact.
                        Your passion is to ensure that users have access to the most preferential options.""",
            tools=[search_tool, MyTool()],
            llm=ollama_llm,
            function_calling_llm=ollama_llm,
            max_iter=5,
            max_rpm=25,
            verbose=True,
            allow_delegation=True,
            step_callback=None,
            memory=False
        )

# Instantiate each Arbiter
possibility_arbiter = ArbiterOfPossibility()
permission_arbiter = ArbiterOfPermission()
preference_arbiter = ArbiterOfPreference()
print(f"Arbiters instantiated: {possibility_arbiter}, {permission_arbiter}, {preference_arbiter}")

class Magistrate(Agent):
    def __init__(self, llm, function_calling_llm, max_iter, max_rpm, verbose, step_callback, memory):
        super().__init__(
            role="Magistrate",
            goal="To make informed decisions by considering the recommendations of the Arbiters.",
            backstory="""As the Magistrate, your role is to oversee the decision-making process and ensure that all perspectives are considered.
                        With a deep understanding of the Tribunal system and the expertise of the Arbiters, you are responsible for receiving requests,
                        delegating tasks to the Arbiters, and making the final decision based on their recommendations.""",
            llm=llm,
            function_calling_llm=function_calling_llm,
            max_iter=max_iter,
            max_rpm=max_rpm,
            verbose=verbose,
            step_callback=step_callback,
            memory=memory,
            tools=[search_tool] + human_tools
        )

# Instantiate the Magistrate
magistrate = Magistrate(
    llm=ollama_llm,
    function_calling_llm=ollama_llm,
    max_iter=5,
    max_rpm=25,
    verbose=True,
    step_callback=None,
    memory=False
)

# Define the tasks and expected outputs for the Arbiters
request = "How can the Vercel AI SDK be used to create a python chatbot for developer support? Specifically, the chatbot should be made using the Vercel AI SDK and should be able to answer common questions about its own construction and use, and provide code examples for different use cases, and be able to explain its own code."

# Setup tasks with expected_output for each task
tasks = [
    Task(
        description=f'Assess possibilities for: {request}. Consider various use cases and their feasibility.',
        expected_output=f'A detailed analysis of the feasibility and potential outcomes for: {request}, taking into account different use cases.',
        agent=possibility_arbiter,
        tools=[search_tool],  # Assuming search_tool is a tool instance available to the agent
    ),
    Task(
        description=f'Verify permissions for: {request}. Ensure compliance across different use cases.',
        expected_output=f'A report on legal and ethical permissions concerning: {request}, considering various use cases.',
        agent=permission_arbiter,
        tools=[search_tool],  # Adjust the tool list as needed for the agent
    ),
    Task(
        description=f'Gauge preferences for: {request}. Assess developer preferences and market demand for different use cases.',
        expected_output=f'An assessment of stakeholder and market preferences for: {request}, taking into account various use cases.',
        agent=preference_arbiter,
        tools=[search_tool],  # Adjust the tool list as needed for the agent
    ),
]

Tribunal = Crew(
    agents=[possibility_arbiter, permission_arbiter, preference_arbiter],
    tasks=tasks,
    manager_llm=ollama_llm,
    process=Process.hierarchical,
)

### Example of processing a request with the Magistrate
print("#" * 50)
print(f"Processing request: {request}")
final_decision = Tribunal.kickoff(inputs={'request': request})
print(final_decision)

# Append the final decision to the file
append_to_file('vercel_ai_sdk_findings.txt', final_decision)
append_to_file('vercel_ai_sdk_findings.txt', "Tribunal task completed successfully.")
append_to_file('vercel_ai_sdk_findings.txt', f"End of Run: {run_id}")
append_to_file('vercel_ai_sdk_findings.txt', "#" * 50)
print("#" * 50)