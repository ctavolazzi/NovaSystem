import os
import logging
import openai
import time
from dotenv import load_dotenv

class NovaChatBot:
    class ConfigManager:
        def __init__(self):
            self.load_api_key()
            self.SYSTEM_PROMPT = "You are a helpful assistant named Nova."
            self.MODEL_NAME = "gpt-3.5-turbo"

        def load_api_key(self):
            load_dotenv()
            self.api_key = os.getenv("OPENAI_API_KEY")
            if not self.api_key:
                raise Exception("API key must be set in environment variables.")

    def __init__(self, config={}):
        self.config = self.ConfigManager()
        self.conversation_history = []

    def stream_to_console(self, message, delay=0.022):
        for char in message:
            print(char, end='', flush=True)
            time.sleep(delay)

    def custom_log(self, message, error_type=None):
        if error_type:
            logging.error(f"Custom Log: {error_type}: {message}")
        else:
            logging.error(f"Custom Log: {message}")

    def fetch_assistant_reply(self, api_payload, stream=False):
        args = {'model': self.config.MODEL_NAME, 'messages': api_payload}
        if stream: args['stream'] = True
        try:
            openai.api_key = self.config.api_key
            response = openai.ChatCompletion.create(**args)
            if stream:
                for chunk in response:
                    yield chunk['choices'][0]['delta'].get('content', '')
            else:
                return response['choices'][0]['message']['content']
        except Exception as e:
            self.custom_log(str(e), type(e).__name__)
            return None

    def display_assistant_reply(self, reply):
        if reply is None:
            self.stream_to_console("An error occurred. Cannot continue.")
        else:
            self.stream_to_console(reply)

    def fetch_and_stream_single_turn(self):
        user_input = input("\n> ")
        if user_input.lower() in ["exit", "q"]:
            return False
        self.conversation_history.append({"role": "user", "content": user_input})
        system_prompt = {"role": "system", "content": self.config.SYSTEM_PROMPT}
        api_payload = [system_prompt] + self.conversation_history
        assistant_reply = self.fetch_assistant_reply(api_payload, stream=True)
        self.display_assistant_reply(assistant_reply)
        return True

if __name__ == "__main__":
    chatbot = NovaChatBot()
    print(f'Nova System Activated...\n"Hello, world!"\nType "exit" or "q" to quit.\n\nPlease enter your first message below to begin chatting with Nova.')
    while chatbot.fetch_and_stream_single_turn():
        pass
