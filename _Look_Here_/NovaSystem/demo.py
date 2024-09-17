import os
import asyncio
import uuid
from datetime import datetime
import sys
from dotenv import load_dotenv

# Add the path to the bots directory to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'core', 'bots'))

# Load the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(dotenv_path)

from Bot_01 import ChatBot

async def run_bot_demo():
    # Get the API key from the .env file
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OpenAI API key not found in .env file. Please add it to the .env file.")
        return

    # Create a unique session ID and folder
    session_id = uuid.uuid4()
    session_folder = os.path.join(os.path.dirname(__file__), f"demo_session_{session_id}")
    os.makedirs(session_folder, exist_ok=True)

    # Set up log and report directories
    log_dir = os.path.join(session_folder, "logs")
    report_dir = os.path.join(session_folder, "reports")

    # Initialize the ChatBot
    bot = ChatBot(log_dir=log_dir, report_directory=report_dir, api_key=api_key)

    print(f"Bot demo started. Session ID: {session_id}")
    print(f"Logs and reports will be saved in: {session_folder}")

    # Simulate some interactions
    prompts = [
        "Hello, what's your name?",
        "What can you do?",
        "Tell me a joke about programming.",
        "What's the weather like today?",
        "Goodbye!"
    ]

    for prompt in prompts:
        print(f"\nUser: {prompt}")
        response = await bot.generate_response(prompt)
        print(f"Bot: {response}")

    # Generate a report
    await bot.generate_report()

    # Simulate writing to offboard memory
    bot.write_offboard_memory("This was a demo session.")

    # Read and print offboard memory
    memory_contents = bot.read_offboard_memory()
    print("\nOffboard Memory Contents:")
    print(memory_contents)

    print("\nBot demo completed. Check the session folder for logs and reports.")

if __name__ == "__main__":
    asyncio.run(run_bot_demo())