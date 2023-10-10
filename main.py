import openai
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def validate_input(attribute, user_input):
    if attribute == 'age':
        return user_input.isdigit() and int(user_input) > 0
    return True  # Placeholder for other attributes

def fetch_openai_chatcompletion(attribute, user_data=None, previous_user_inputs=None):
    messages = [
        {
            'role': 'system',
            'content': 'You are a snarky AI named Marvin. Your goal is to help the user get entered into the NOVA System.'
        },
        {
            'role': 'user',
            'content': f'Please return only a funny and sardonic question asking the user for the following attribute: {attribute}. Please reply with ONLY an engaging and unusual question requesting the attribute from the user.'
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

def stream_to_console(message, delay=0.02):
    for char in message:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def conduct_conversation():
    user_setup = read_json_file('user_setup.json')
    user_data = {}
    previous_user_inputs = []

    for attribute in user_setup['user'].keys():
        valid_input = False
        attempts = 0
        while not valid_input:
            question = fetch_openai_chatcompletion(attribute, user_data, previous_user_inputs)
            stream_to_console(question)
            user_input = input('> ')
            previous_user_inputs.append(user_input)
            valid_input = validate_input(attribute, user_input)

            if valid_input:
                user_data[attribute] = user_input if attribute != 'age' else int(user_input)
            else:
                if attempts >= 3:
                    snarky_reply = fetch_openai_chatcompletion("incorrect age", user_data, previous_user_inputs)
                    stream_to_console(snarky_reply)
                else:
                    stream_to_console("Invalid input. Please try again.")
                attempts += 1

    write_json_file('user.json', user_data)
    stream_to_console("User data has been saved.")

# Uncomment the following line to run the conversation.
conduct_conversation()
