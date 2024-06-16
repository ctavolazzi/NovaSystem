# Import necessary modules
from autogen import AssistantAgent, UserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
import os
from pathlib import Path
import logging

# Set up logger
logging.basicConfig(filename='app.log', level=logging.INFO)

# Define configuration and work directory
llm_config = {
    "config_list": [{"model": "gpt-4", "api_key": os.environ["OPENAI_API_KEY"]}]
}
work_dir = Path("coding")
work_dir.mkdir(parents=True, exist_ok=True)

# Initialize assistants and code executor
try:
    assistant = AssistantAgent("assistant", llm_config=llm_config)
except Exception as e:
    logging.error(f"AssistantAgent initialization failed with error: {str(e)}")
    raise

code_executor = LocalCommandLineCodeExecutor(work_dir=work_dir)

# Initialize user proxy agent
try:
    user_proxy = UserProxyAgent(
        "user_proxy", code_execution_config={"executor": code_executor}
    )
except Exception as e:
    logging.error(f"UserProxyAgent initialization failed with error: {str(e)}")
    raise

# Start the chat
def process_query(assistant, query):
    try:
        response = assistant.send_message(query)
        return response
    except Exception as e:
        logging.error(f"Assistant error while processing query: {str(e)}")
        raise

query = "Plot a chart of NVDA and TESLA stock price change YTD."
response = process_query(assistant, query)
user_proxy.send_message(response)