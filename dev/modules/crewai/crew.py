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


import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Assuming 'SerperDevTool' can be repurposed for searching creative writing insights or replaced with a suitable tool
story_tool = SerperDevTool()

# Agents focused on different aspects of story creation
plot_developer = Agent(
    role='Plot Developer',
    goal='Develop the plot for "Teleport Massive"',
    verbose=True,
    memory=True,
    backstory=(
        "Obsessed with crafting intricate stories, you delve into the narrative depths to sketch out the backbone of 'Teleport Massive'."
    ),
    tools=[story_tool],
    allow_delegation=True
)

character_creator = Agent(
    role='Character Creator',
    goal='Design characters for "Teleport Massive"',
    verbose=True,
    memory=True,
    backstory=(
        "With a keen eye for psychology and detail, you breathe life into the characters that will inhabit the world of 'Teleport Massive'."
    ),
    tools=[story_tool],
    allow_delegation=True
)

world_builder = Agent(
    role='World Builder',
    goal='Construct the world of "Teleport Massive" set in 2111',
    verbose=True,
    memory=True,
    backstory=(
        "A visionary architect of worlds, you sculpt the setting of 2111 with a blend of imagination and futurism."
    ),
    tools=[story_tool],
    allow_delegation=True
)

story_writer = Agent(
    role='Story Writer',
    goal='Weave together the plot, characters, and setting into the story of "Teleport Massive"',
    verbose=True,
    memory=True,
    backstory=(
        "With the quill of creativity and the ink of passion, you narrate the tale of 'Teleport Massive', bringing the collective vision to life."
    ),
    tools=[story_tool],
    allow_delegation=False
)

# Tasks for each aspect of story creation
plot_task = Task(
    description="Create an engaging and dynamic plot for 'Teleport Massive'.",
    expected_output="A detailed plot outline.",
    tools=[story_tool],
    agent=plot_developer,
)

character_task = Task(
    description="Develop deep and compelling characters for 'Teleport Massive'.",
    expected_output="Character bios and arcs.",
    tools=[story_tool],
    agent=character_creator,
)

world_task = Task(
    description="Design the futuristic world of 2111 for 'Teleport Massive'.",
    expected_output="Descriptions of the world's setting, technology, and society.",
    tools=[story_tool],
    agent=world_builder,
)

story_task = Task(
    description="Combine all elements into the complete story of 'Teleport Massive'.",
    expected_output="The full manuscript of 'Teleport Massive'.",
    tools=[story_tool],
    agent=story_writer,
    async_execution=False,
    output_file='TeleportMassiveStory.md'
)

# Assemble the crew and define the sequential process
crew = Crew(
    agents=[plot_developer, character_creator, world_builder, story_writer],
    tasks=[plot_task, character_task, world_task, story_task],
    process=Process.sequential
)

# Kickoff the crew task execution (placeholder, replace with actual logic)
result = crew.kickoff(inputs={'story': 'Teleport Massive'})
print(result)
