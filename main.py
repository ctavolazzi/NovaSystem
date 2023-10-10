# Final code with actual OpenAI ChatCompletion API calls
# Note: This is a Python code snippet and assumes you have imported required libraries like openai, json, and os.

import openai
import json
import os
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

def fetch_openai_chatcompletion(attribute):
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
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

def conduct_conversation():
    user_setup = read_json_file('user_setup.json')
    user_data = {}
    for attribute in user_setup['user'].keys():
        valid_input = False
        while not valid_input:
            question = fetch_openai_chatcompletion(attribute)
            user_input = input(question)
            valid_input = validate_input(attribute, user_input)
            if valid_input:
                user_data[attribute] = user_input if attribute != 'age' else int(user_input)
            else:
                print("Invalid input. Please try again.")
    write_json_file('user.json', user_data)
    print("User data has been saved.")

# Uncomment the following line to run the conversation.
conduct_conversation()
