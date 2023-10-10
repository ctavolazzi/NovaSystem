import time
import threading
import openai
import json
import os
from dotenv import load_dotenv

load_dotenv()
# Get the OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

class NovaHelper:
    _default_delay = 0.022

    def __init__(self):
        self.classification = 'NovaHelper'
        self.stop_flag = threading.Event()
        self.user = {}

    def stream_to_console(self, message, delay=_default_delay):
        for char in message:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()

    def stc(self, message, delay=_default_delay):
        self.stream_to_console(message, delay)

    def loading_animation(self, duration=3):
        self.start_loading_indicator()
        time.sleep(duration)
        self.stop_loading_indicator()

    def ask_and_set_user_property(self, question, property_name):
        self.stc(question)
        user_input = input("> ")
        self.user[property_name] = user_input

    def fetch_openai_response(self, prompt):
        # Call OpenAI API here to get dynamic responses
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=150,
            messages=[{'role': 'system', 'content': 'You are a snarky and sardonic assitant named Marvin. You are here to help your master, Nova, an all-powerful AI, to help it acquaint himself with itself with a new user.'}, {'role': 'user', 'content': prompt}]
        )
        return response

    def extract_openai_response_content_with_optional_callback(self, response, callback=None):
        if not callback:
            return response["choices"][0]["message"]["content"]
        else:
            return callback(response["choices"][0]["message"]["content"])

    def fetch_and_extract_and_display_openai_response(self, prompt):
        response = self.fetch_openai_response(prompt)
        response_content = response["choices"][0]["message"]["content"]
        self.stc(response_content)

    def chat_with_user(self):
        self.stc("Welcome to the NovaVerse!")
        self.loading_animation()

        # Predefined first question
        self.ask_and_set_user_property("What is your name?", "name")

        # Fake loading to set user expectation
        self.loading_animation()

        # Dynamic question based on user's name
        next_prompt = f"Nice to meet you, {self.user['name']}. What brings you here?"
        ai_response = self.fetch_openai_response(next_prompt)

        self.stc(ai_response)

        # ... continue the conversation and build the user object
        # Save user object
        with open('user.json', 'w') as f:
            json.dump(self.user, f)

    def conduct_conversation(self):
        self.stc("Welcome to the NovaVerse!")
        self.loading_animation()

        # Predefined first question
        self.ask_and_set_user_property("What is your name?", "name")

        # Fake loading to set user expectation
        self.loading_animation()

        # Dynamic question based on user's name
        next_prompt = f"Nice to meet you, {self.user['name']}. What brings you here?"
        self.fetch_and_extract_and_display_openai_response(next_prompt)

        # Save user object
        with open('user.json', 'w') as f:
            json.dump(self.user, f)

    def set_up_user(self):
        # Check if user.json exists
        if not os.path.exists('user.json'):
            # If not, ask for user's name
            self.ask_and_set_user_property("What is your name?", "name")
        pass

    def ask_and_set_user_property(self, question, property_name):
        self.stc(question)
        user_input = input("> ")
        self.user[property_name] = user_input

    def start_loading_indicator(self):
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self.loading_indicator)
        self.thread.start()

    def stop_loading_indicator(self):
        self.stop_flag.set()
        self.thread.join()

    def wait_for_and_return_user_input(self):
        user_input = input("> ")
        return user_input

    def loading_indicator(self):
        while not self.stop_flag.is_set():
            print("\033[?25h", end='', flush=True)
            if self.stop_flag.wait(timeout=0.33):
                break
            print("\033[?25l", end='', flush=True)
            if self.stop_flag.wait(timeout=0.33):
                break
        print("\033[?25h", end='', flush=True)

if __name__ == "__main__":
    helper = NovaHelper()
    helper.conduct_conversation()
