# Import required libraries
import time
import openai
import json
import os
from dotenv import load_dotenv

# Initialize the environment
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize user object
user = {}

# Initialize delay for text streaming
default_delay = 0.022

# Function to stream text to console
def stream_to_console(message, delay=default_delay):
    for char in message:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

# Function to fetch OpenAI response
def fetch_openai_response(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {'role': 'system', 'content': 'You are a snarky and sardonic assistant named Marvin. You are here to help your master, Nova, an all-powerful AI, to help it acquaint himself with a new user.'},
            {'role': 'user', 'content': prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]

# Function to conduct conversation
def conduct_conversation():
    stream_to_console("Welcome to the NovaVerse!")
    time.sleep(3)  # Simulate loading time

    # Predefined first question
    name_prompt = "What is your name?"
    stream_to_console(name_prompt)
    user_input = input("> ")
    user['name'] = user_input

    # Use OpenAI for dynamic response
    next_prompt = f"Nice to meet you, {user['name']}. What brings you here?"
    ai_response = fetch_openai_response(next_prompt)
    stream_to_console(ai_response)

    # Save user object
    with open('user.json', 'w') as f:
        json.dump(user, f)

# Run the conversation
conduct_conversation()
