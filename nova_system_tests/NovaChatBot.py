import os
import logging
import openai
<<<<<<< HEAD
<<<<<<< HEAD
=======
import time
>>>>>>> 5da575c (Initial commit)
=======
import time
>>>>>>> temp-branch-to-save-detached-head
from dotenv import load_dotenv
from NovaHelper import stc
from NovaConfigManager import NovaConfigManager

class NovaChatBot:
<<<<<<< HEAD
<<<<<<< HEAD
    _DEFAULT_SYSTEM_PROMPT = "You are an instance of a helpful assistant named Nova."

    def __init__(self, config=None):
        self.config_manager = NovaConfigManager()
        self.conversation_history = []
        self.load_config(config)
        self.initialize_openai_api()

    def initialize_openai_api(self):
        load_dotenv()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def load_config(self, config):
        if config:
            stc(f'Config provided.\n')
            self.config_manager.load_config(self, config)
        else:
            stc(f'No config provided.\n')
            self.config_manager.load_config(self, self.config_manager._DEFAULT_CONFIG)
            self.config_manager.add_config_attribute('system_prompt', self._DEFAULT_SYSTEM_PROMPT)

    def add_message_to_history(self, role, content):
        self.conversation_history.append({"role": role, "content": content})
=======
=======
>>>>>>> temp-branch-to-save-detached-head
    _DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant named Nova."

    def __init__(self, config=None):
        self.config_manager = NovaConfigManager()
        if config:
            stc(f'Config provided.\n')
            self.config_manager.load_config(self, config)
            # stc(f'Loaded Config: {self.config}')
        else:
            stc(f'No config provided.\n')
            # stc(f'Initializing with default config...\n')
            self.config_manager.load_config(self, self.config_manager._DEFAULT_CONFIG)
            self.config_manager.add_config_attribute('system_prompt', self._DEFAULT_SYSTEM_PROMPT)
            # stc(f'Loaded Config: {self.config}')
        self.conversation_history = []

    def custom_log(self, message, error_type=None):
        if error_type:
            logging.error(f"Custom Log: {error_type}: {message}\n")
        else:
            logging.error(f"Custom Log: {message}\n")
<<<<<<< HEAD
>>>>>>> 5da575c (Initial commit)
=======
>>>>>>> temp-branch-to-save-detached-head

    def fetch_assistant_reply(self, api_payload, stream=False):
        args = {'model': self.config["model"], 'messages': api_payload}
        if stream: args['stream'] = True
        try:
<<<<<<< HEAD
<<<<<<< HEAD
=======
            openai.api_key = self.config["openai_api_key"]
>>>>>>> 5da575c (Initial commit)
=======
            openai.api_key = self.config["openai_api_key"]
>>>>>>> temp-branch-to-save-detached-head
            response = openai.ChatCompletion.create(**args)
            if stream:
                for chunk in response:
                    yield chunk['choices'][0]['delta'].get('content', '')
            else:
                return response['choices'][0]['message']['content']
        except Exception as e:
<<<<<<< HEAD
<<<<<<< HEAD
            logging.error(f"Custom Log: {type(e).__name__}: {str(e)}\n")
=======
            self.custom_log(str(e), type(e).__name__)
>>>>>>> 5da575c (Initial commit)
=======
            self.custom_log(str(e), type(e).__name__)
>>>>>>> temp-branch-to-save-detached-head
            return None

    def display_assistant_reply(self, reply):
        if reply is None:
            print("An error occurred. Cannot continue.")
        else:
            stc(reply)

    def fetch_and_stream_single_turn(self, user_input=None):
        if user_input:
<<<<<<< HEAD
<<<<<<< HEAD
            self.add_message_to_history("user", user_input)
=======
            self.conversation_history.append({"role": "user", "content": user_input})
>>>>>>> 5da575c (Initial commit)
=======
            self.conversation_history.append({"role": "user", "content": user_input})
>>>>>>> temp-branch-to-save-detached-head
        else:
            user_input = input("\n> ")
        if user_input.lower() in ["exit", "q"]:
            return False
<<<<<<< HEAD
<<<<<<< HEAD

        self.add_message_to_history("user", user_input)
=======
        self.conversation_history.append({"role": "user", "content": user_input})
>>>>>>> 5da575c (Initial commit)
=======
        self.conversation_history.append({"role": "user", "content": user_input})
>>>>>>> temp-branch-to-save-detached-head
        system_prompt = {"role": "system", "content": self.config["system_prompt"]}
        api_payload = [system_prompt] + self.conversation_history
        assistant_reply = self.fetch_assistant_reply(api_payload, stream=True)
        self.display_assistant_reply(assistant_reply)
        return True

    def test(self):
      stc(f'\nTesting NovaChatBot...')
<<<<<<< HEAD
<<<<<<< HEAD
=======
      # stc(f'Test Config: {self.config}\n')
>>>>>>> 5da575c (Initial commit)
=======
      # stc(f'Test Config: {self.config}\n')
>>>>>>> temp-branch-to-save-detached-head

if __name__ == "__main__":
    chatbot = NovaChatBot()
    chatbot.test()
<<<<<<< HEAD
<<<<<<< HEAD
    while chatbot.fetch_and_stream_single_turn():
        pass










# import os
# import logging
# import openai
# import time
# from dotenv import load_dotenv
# from NovaHelper import stc
# from NovaConfigManager import NovaConfigManager

# load_dotenv()
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# class NovaChatBot:
#     _DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant named Nova."

#     def __init__(self, config=None):
#         self.config_manager = NovaConfigManager()
#         if config:
#             stc(f'Config provided.\n')
#             self.config_manager.load_config(self, config)
#             # stc(f'Loaded Config: {self.config}')
#         else:
#             stc(f'No config provided.\n')
#             # stc(f'Initializing with default config...\n')
#             self.config_manager.load_config(self, self.config_manager._DEFAULT_CONFIG)
#             self.config_manager.add_config_attribute('system_prompt', self._DEFAULT_SYSTEM_PROMPT)
#             # stc(f'Loaded Config: {self.config}')
#         self.conversation_history = []

#     def custom_log(self, message, error_type=None):
#         if error_type:
#             logging.error(f"Custom Log: {error_type}: {message}\n")
#         else:
#             logging.error(f"Custom Log: {message}\n")

#     def fetch_assistant_reply(self, api_payload, stream=False):
#         args = {'model': self.config["model"], 'messages': api_payload}
#         if stream: args['stream'] = True
#         try:
#             openai.api_key = os.getenv("OPENAI_API_KEY")
#             response = openai.ChatCompletion.create(**args)
#             if stream:
#                 for chunk in response:
#                     yield chunk['choices'][0]['delta'].get('content', '')
#             else:
#                 return response['choices'][0]['message']['content']
#         except Exception as e:
#             self.custom_log(str(e), type(e).__name__)
#             return None

#     def display_assistant_reply(self, reply):
#         if reply is None:
#             print("An error occurred. Cannot continue.")
#         else:
#             stc(reply)

#     def fetch_and_stream_single_turn(self, user_input=None):
#         if user_input:
#             self.conversation_history.append({"role": "user", "content": user_input})
#         else:
#             user_input = input("\n> ")
#         if user_input.lower() in ["exit", "q"]:
#             return False
#         self.conversation_history.append({"role": "user", "content": user_input})
#         system_prompt = {"role": "system", "content": self.config["system_prompt"]}
#         api_payload = [system_prompt] + self.conversation_history
#         assistant_reply = self.fetch_assistant_reply(api_payload, stream=True)
#         self.display_assistant_reply(assistant_reply)
#         return True

#     def test(self):
#       stc(f'\nTesting NovaChatBot...')
#       # stc(f'Test Config: {self.config}\n')

# if __name__ == "__main__":
#     chatbot = NovaChatBot()
#     chatbot.test()
#     # stc(f'Nova System Activated with config:\n{chatbot.config}\n"Hello, world!"\nType "exit" or "q" to quit.\n\nPlease enter your first message below to begin chatting with Nova.')
#     while chatbot.fetch_and_stream_single_turn():
#         pass
=======
    # stc(f'Nova System Activated with config:\n{chatbot.config}\n"Hello, world!"\nType "exit" or "q" to quit.\n\nPlease enter your first message below to begin chatting with Nova.')
    while chatbot.fetch_and_stream_single_turn():
        pass
>>>>>>> 5da575c (Initial commit)
=======
    # stc(f'Nova System Activated with config:\n{chatbot.config}\n"Hello, world!"\nType "exit" or "q" to quit.\n\nPlease enter your first message below to begin chatting with Nova.')
    while chatbot.fetch_and_stream_single_turn():
        pass
>>>>>>> temp-branch-to-save-detached-head
