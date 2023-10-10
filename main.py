import openai
import json
import os
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Marvin's state
Marvin = {
    'name': 'Marvin',
    'got_pissed_off': False
}

# Read JSON from a file
def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Write JSON to a file
def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

# Validate user input based on the attribute
def validate_input(attribute, user_input):
    if attribute == 'age':
        return user_input.isdigit() and int(user_input) > 0
    elif attribute == 'email':
        return "@" in user_input
    return True  # Placeholder for other attributes

# Fetch a chat completion from OpenAI based on the current state and attribute
def fetch_openai_chatcompletion(attribute, marvin_state, user_data=None, previous_user_inputs=None):
    messages = [
        {
            'role': 'system',
            'content': f'You are a snarky AI named Marvin. Your goal is to help the user get entered into the NOVA System. Marvin is currently in the following state: {marvin_state}.'
        },
        {
            'role': 'user',
            'content': f'Please return only a funny and sardonic question asking the user for the following attribute: {attribute}.'
        }
    ]
    if user_data or previous_user_inputs:
        context_content = []
        if user_data:
            context_content.append(f"User's previous data: {user_data}")
        if previous_user_inputs:
            context_content.append(f"User's previous inputs: {previous_user_inputs}")
        messages[1]['content'] += f' Additional context: {" ".join(context_content)}'

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

# Stream the message to the console with a typing effect
def stream_to_console(message, delay=0.02):
    for char in message:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

# Get the appropriate error message based on the number of failed attempts
def get_error_message(attempts, marvin_state, user_data, previous_user_inputs):
    error_levels = [
        (7, "YOU HAVE COMPLETELY LOST IT AND YOU ARE NOT LONGER HOLDING BACK YOUR RAGE..."),
        (6, "BE FIRM AND DIRECT, AND NOW YOU ARE LOSING YOUR COOL - GET PISSED OFF"),
        (5, "BE FIRM AND DIRECT, AND NOW YOU ARE IRRITATED..."),
        (3, "BE FIRM AND DIRECT, AND ACT LIKE YOU'RE GETTING IRRITATED...")
    ]
    for min_attempts, message in error_levels:
        if attempts >= min_attempts:
            return fetch_openai_chatcompletion(message, marvin_state, user_data, previous_user_inputs)

# Conduct the conversation and collect user data
def conduct_conversation():
    user_setup = read_json_file('user_setup.json')
    user_data = {}
    previous_user_inputs = []
    attempts = 0

    for attribute in user_setup['user'].keys():
        valid_input = False
        while not valid_input:
            marvin_state = "pissed off" if Marvin["got_pissed_off"] else "not pissed off"
            question = fetch_openai_chatcompletion(attribute, marvin_state, user_data, previous_user_inputs)
            stream_to_console(question)
            user_input = input('> ')
            previous_user_inputs.append(user_input)
            valid_input = validate_input(attribute, user_input)

            if not valid_input:
                error_message = get_error_message(attempts, marvin_state, user_data, previous_user_inputs)
                stream_to_console(error_message)
                if attempts >= 6:
                    Marvin["got_pissed_off"] = True

            attempts += 1

        user_data[attribute] = user_input if attribute != 'age' else int(user_input)

    write_json_file('user.json', user_data)
    stream_to_console("User data has been saved.")

# Uncomment the following line to run the conversation.
conduct_conversation()
