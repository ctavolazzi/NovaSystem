from uuid import uuid4
from collections import deque
from get_custom_openai_chat_completions_response import get_custom_openai_chat_completions_response
import time
import logging

class Bot:
    DEFAULT_CONFIG = {
        "name": "Botticus",
        "system_message": "You are a bot in a system that helps users understand data, answer questions, and make decisions.",
    }

    def __init__(self, system_message=DEFAULT_CONFIG["system_message"]):
        self.name = self.DEFAULT_CONFIG["name"]
        self._id = str(uuid4())
        self._history_size = 5
        self._response_history = deque()
        self._message_history = deque(maxlen=self._history_size)
        self._system_message = system_message
        self._last_response = None
        self._last_thought = None
        self._time_of_instantiation = time.time()
        self._log_bot_creation()
        self.number_of_responses_generated = 0
        self.think_about(self._system_message)

    def _log_bot_creation(self):
        logging.info(f"Bot {self.name} id {self._id} created at {self._time_of_instantiation}")

    def _get_openai_chat_completions_response(self, context):
        messages_to_send_to_openai = [{"role": "system", "content": self._system_message}]

        if isinstance(context, str):
            context = [{"role": "user", "content": context}]
        elif isinstance(context, list):
            for item in context:
                if hasattr(item, "role") and item.role in ["system", "user", "assistant"]:
                    messages_to_send_to_openai.append(item)
        else:
            raise Exception("Invalid context type")

        try:
            response = get_custom_openai_chat_completions_response(messages_to_send_to_openai)
            self.number_of_responses_generated += 1
        except Exception as e:
            logging.error(f"An error occurred when making a request to the OpenAI API: {e}")
            raise e

        self._response_history.append(response)
        return response

    def think_about(self, str_input):
        response = self._get_openai_chat_completions_response(str_input)
        logging.info(f"Bot {self.name} is thinking about {str_input} and wants to say {response.choices[0].message.content}")
        self._last_thought = response
        # print(f"{self.name} thinks: {response.choices[0].message.content}")

    def respond_to(self, str_input):
        response = self._get_openai_chat_completions_response(str_input)
        logging.info(f"Bot {self.name} is responding to {str_input} with {response.choices[0].message.content}")
        self._last_response = response
        # print(f"{self.name} says: {response.choices[0].message.content}")

    def respond_with_context(self, context):
        response = self._get_openai_chat_completions_response(context)
        logging.info(f"Bot {self.name} is responding to {context} with {response.choices[0].message.content}")
        self._last_response = response
        # print(f"{self.name} says: {response.choices[0].message.content}")

    def identify(self):
        print(f"I am {self.name} and my id is {self._id}")
        logging.info(f"I am {self.name} and my id is {self._id}")

    # Getters and setters
    def get_last_response(self):
        return self._last_response

    def get_last_thought(self):
        return self._last_thought

    def get_name(self):
        return self.name

    def get_id(self):
        return self._id

    def get_time_of_instantiation(self):
        return self._time_of_instantiation

    def get_system_message(self):
        return self._system_message

    def get_message_history(self):
        return list(self._message_history)

    def get_history_size(self):
        return self._history_size

    def set_name(self, name):
        if not isinstance(name, str):
            raise TypeError("Name must be a string.")
        self.name = name
        logging.info(f"Bot {self._id} name changed to {self.name}")

    def set_system_message(self, system_message):
        if not isinstance(system_message, str):
            raise TypeError("System message must be a string.")
        self._system_message = system_message
        logging.info(f"Bot {self._id} system message changed to {self._system_message}")

    def set_history_size(self, history_size):
        if not isinstance(history_size, int):
            raise TypeError("History size must be an integer.")
        self._history_size = history_size
        self._message_history = deque(maxlen=self._history_size)  # Reinitialize message history with new size
        logging.info(f"Bot {self._id} history size changed to {self._history_size}")

    def set_message_history(self, message_history):
        if not isinstance(message_history, list):
            raise TypeError("Message history must be a list.")
        self._message_history = deque(message_history, maxlen=self._history_size)
        logging.info(f"Bot {self._id} message history changed")

    def set_last_response(self, last_response):
        if not isinstance(last_response, str):
            raise TypeError("Last response must be a string.")
        self._last_response = last_response
        logging.info(f"Bot {self._id} last response changed")

    # Overloaded methods
    def __str__(self):
        return f"Bot {self.name} id {self._id} created at {self._time_of_instantiation}"

    def __repr__(self):
        return f"Bot {self.name} id {self._id} created at {self._time_of_instantiation}"

    def __eq__(self, other):
        if not isinstance(other, Bot):
            return NotImplemented
        return self._id == other._id

    def __ne__(self, other):
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def print_state(self):
        return f"""
    ╔═══════════════════════════════════════════════╗
    ║              BOT STATUS REPORT                ║
    ║ Response No: {self.number_of_responses_generated}
    ╠═══════════════════════════════════════════════╣
    ║ Name: {self.name}
    ║ id: {self._id}
    ║ Time of instantiation: {self._time_of_instantiation}
    ║ History size: {self._history_size}
    ║ System message: {self._system_message}
    ║ Message history: {self._message_history}
    ║ Last response: {'None' if self._last_response is None else self._last_response.choices[0].message.content}
    ║ Last thought: {'None' if self._last_thought is None else self._last_thought.choices[0].message.content}

    ╚═══════════════════════════════════════════════╝
        """

if __name__ == "__main__":
    bot = Bot("You are a monster that loves cookies.")
    bot.identify()
    print(bot.print_state())
