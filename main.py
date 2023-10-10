import openai
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

Marvin = {
    'name': 'Marvin',
    'got_pissed_off': False
}

def read_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def validate_input(attribute, user_input):
    if attribute == 'age':
        return user_input.isdigit() and int(user_input) > 0
    elif attribute == 'email':
        return "@" in user_input
    return True  # Placeholder for other attributes

def fetch_openai_chatcompletion(attribute, user_data=None, previous_user_inputs=None):
    messages = [
        {
            'role': 'system',
            'content': f'You are a snarky AI named Marvin. Your goal is to help the user get entered into the NOVA System. Marvin is {"pissed off" if Marvin["got_pissed_off"] else "not pissed off"}.'
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
                if attempts >= 3 & attempts < 5:
                    snarky_reply = fetch_openai_chatcompletion("incorrect input, over max attempts; BE FIRM AND DIRECT, AND ACT LIKE YOU'RE GETTING IRRITATED, BUT YOU'RE STILL WANTING TO BE NICE", user_data, previous_user_inputs)
                    stream_to_console(snarky_reply)
                elif attempts >= 5:
                    serious_reply = fetch_openai_chatcompletion("incorrect input, over max attempts; BE FIRM AND DIRECT, AND NOW YOU ARE IRRITATED WITH THE USER AND YOU ARE GETTING NOTICABLY FRUSTRATED", user_data, previous_user_inputs)
                    stream_to_console(serious_reply)
                elif attempts >= 6:
                    warning_reply = fetch_openai_chatcompletion("incorrect input, over max attempts; BE FIRM AND DIRECT, AND NOW YOU ARE LOSING YOUR COOL - GET PISSED OFF", user_data, previous_user_inputs)
                    Marvin.got_pissed_off = True
                    stream_to_console(warning_reply)
                elif attempts >= 7:
                    pissed_off_reply = fetch_openai_chatcompletion("incorrect input, over max attempts; YOU HAVE COMPLETELY LOST IT AND YOU ARE NOT LONGER HOLDING BACK YOUR RAGE AT THE USER FOR THEIR REPEATED REFUSAL TO ANSWER YOUR SIMPLE QUESTION", user_data, previous_user_inputs)
                    stream_to_console(pissed_off_reply)
                else:
                    guiding_reply = fetch_openai_chatcompletion("incorrect input, but under max attempts", user_data, previous_user_inputs)
                    # steering_message = "Hmm, that doesn't quite work. Let's try this again."
                    stream_to_console(guiding_reply)
                attempts += 1

    write_json_file('user.json', user_data)
    stream_to_console("User data has been saved.")

# Uncomment the following line to run the conversation.
conduct_conversation()
