import os
import json
import openai  # Ensure you've installed the openai package
from dotenv import load_dotenv

load_dotenv()

class ConfigManager:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key  # Setting the API key for OpenAI

class StateManager:
    def __init__(self):
        self.state = {
            'mood': 'neutral',
            'engagement_level': 'medium',
            'last_user_input': None,
            'error_count': 0,
            'conversation_topic': None
        }

    def update_state(self, key, value):
        self.state[key] = value

    def query_state(self, key):
        return self.state.get(key, "Unknown")
# Updated Implementation incorporating all the changes

import os
import json
# Commenting out OpenAI for the skeleton; uncomment in the actual implementation
# import openai

class BBot:
    def __init__(self):
        self.state = {
            'mood': 'neutral',
            'engagement_level': 'medium',
            'last_user_input': None,
            'error_count': 0,
            'conversation_topic': None
        }

    def update_state(self, key, value):
        self.state[key] = value

    def get_error_message(self, attempts):
        error_messages = [
            (1, "Please try again."),
            (2, "Error: Invalid input, please try again."),
            (3, "Error: Invalid input, please try again. [OpenAI Enhanced]"),
            (4, "[Fully OpenAI Generated Error]")
        ]
        for min_attempts, message in error_messages:
            if attempts >= min_attempts:
                return message

    def fetch_openai_chatcompletion(self, attribute):
        # Placeholder for actual OpenAI API call
        return f"Please provide the following information:\n{attribute}: "

def read_json_file(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def validate_input(attribute, user_input):
    if attribute == 'age':
        return user_input.isdigit() and int(user_input) > 0
    elif attribute == 'email':
        return "@" in user_input
    return True  # Placeholder for other attributes

def conduct_conversation():
    bbot = BBot()
    user_data = {}

    # Check if user.json exists and is readable
    if read_json_file('user.json'):
        user_data = read_json_file('user.json')
        print(f"Hello again, {user_data.get('name', 'there')}! Let's continue, shall we?")
    else:
        user_setup = read_json_file('user_setup.json')
        if user_setup is None:
            print("Error: user_setup.json not found.")
            return

    previous_user_inputs = []
    max_attempts = 4

    for attribute in user_setup['user'].keys():
        if attribute in user_data:
            continue

        attempts = 0
        valid_input = False

        while not valid_input and attempts < max_attempts:
            question = bbot.fetch_openai_chatcompletion(attribute)
            print(question)
            user_input = input("> ")
            previous_user_inputs.append(user_input)

            valid_input = validate_input(attribute, user_input)
            if not valid_input:
                attempts += 1
                error_message = bbot.get_error_message(attempts)
                print(error_message)

        if valid_input:
            user_data[attribute] = user_input if attribute != 'age' else int(user_input)

    write_json_file('user.json', user_data)
    print("User data has been saved.")


def main():
    config = ConfigManager()
    state_manager = StateManager()
    bbot = BBot(config, state_manager)

    while True:
        user_input = input("You: ")
        bbot.add_message("user", user_input)
        rule_based_response = bbot.rule_based_answer(user_input)

        if rule_based_response:
            print(f"BBot: {rule_based_response}")
        else:
            gpt_response = bbot.get_gpt_response()
            print(f"BBot: {gpt_response}")

        if user_input.lower() == "quit":
            break

if __name__ == "__main__":
    main()
