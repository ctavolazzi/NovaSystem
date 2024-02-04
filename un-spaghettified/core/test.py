import sys
from autogen import AssistantAgent, UserProxyAgent
from dotenv import load_dotenv
import os

# Load the .env info
load_dotenv()  
api_key = os.getenv('OPENAI_API_KEY')

print(sys.path)
print("pyautogen imported successfully")

config_list = [
    {
        "model": "gpt-3.5-turbo",
        "api_key": api_key
    }
    # Add more configurations if needed
]

# Create AssistantAgent with the llm_config
assistant = AssistantAgent(
    name="assistant",
    llm_config={
        "seed": 42,
        "config_list": config_list,
        "temperature": 0,
    }
)

# Create a UserProxyAgent with configuration for code execution
user_proxy = UserProxyAgent(
    name="user_proxy",
    code_execution_config={"work_dir": "coding", "use_docker": False}  # Set to True to run code in docker
)

# Initiate a chat between the two agents to perform a task
user_proxy.initiate_chat(assistant, message="Plot a chart of NVDA and TESLA stock price change YTD.")
