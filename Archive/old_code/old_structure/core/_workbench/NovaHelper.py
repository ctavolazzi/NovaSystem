import time
import threading
import openai
import json

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
        return "OpenAI API Response for: " + prompt

    def conduct_conversation(self):
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

    def start_loading_indicator(self):
        self.stop_flag.clear()
        self.thread = threading.Thread(target=self.loading_indicator)
        self.thread.start()

    def stop_loading_indicator(self):
        self.stop_flag.set()
        self.thread.join()

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
